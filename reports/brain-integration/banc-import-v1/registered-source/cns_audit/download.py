"""Verified resumable source downloads; preserve failures and the disk reserve."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path

RESERVE = 2 * 2**30
CHUNK = 64 * 2**20


def hashes(path):
    sha, md5 = hashlib.sha256(), hashlib.md5()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            sha.update(b); md5.update(b)
    return {'sha256': sha.hexdigest(), 'md5': md5.hexdigest(), 'bytes': Path(path).stat().st_size}


def atomic_json(path, value, reserve=RESERVE):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + '\n').encode()
    if shutil.disk_usage(path.parent).free - len(raw) < reserve:
        raise OSError('Paused: preserving free-space reserve')
    temp = path.with_name(path.name + '.tmp')
    with temp.open('wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    temp.replace(path)


def open_request(url, headers=None, method='GET'):
    req = urllib.request.Request(url, headers={'User-Agent': 'FlyGarden registered BANC source audit'} | (headers or {}), method=method)
    return urllib.request.urlopen(req, timeout=45)


def verified_download(source, destination, *, reserve=RESERVE, chunk_size=CHUNK, progress=None):
    """Append only after identity/resume validation; publish only after full MD5.

    Journaled chunks are fsynced before acknowledgement. An uncommitted tail is
    retained separately on resume, never silently removed. Exact ranged responses
    are required, so a server cannot append the wrong byte interval.
    """
    if not isinstance(source['bytes'], int) or source['bytes'] <= 0 or chunk_size <= 0:
        raise ValueError('Positive source length and chunk size required')
    if len(source['md5']) != 32 or any(c not in '0123456789abcdef' for c in source['md5']):
        raise ValueError('Registered lowercase MD5 required')
    destination = Path(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    lock = destination.with_name(destination.name + '.lock')
    with lock.open('a+b') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if destination.exists():
            identity = hashes(destination)
            if identity['bytes'] != source['bytes'] or identity['md5'] != source['md5']:
                raise ValueError('Existing source differs; preserved without replacement')
            return identity | {'cached': True}
        partial = destination.with_name(destination.name + '.part')
        journal = destination.with_name(destination.name + '.download.json')
        pinned = {k: source[k] for k in ('url', 'bytes', 'md5')}
        state = {'source': pinned, 'chunk_size': chunk_size, 'chunks': [], 'offset': 0, 'status': 'downloading'}
        if journal.exists():
            state = json.loads(journal.read_text())
            if state['source'] != pinned or state['chunk_size'] != chunk_size:
                raise ValueError('Resume identity differs; partial source preserved')
            if not partial.exists():
                raise ValueError('Journal has no partial file')
            with partial.open('rb') as f:
                offset = 0
                for c in state['chunks']:
                    b = f.read(c['bytes']); offset += len(b)
                    if len(b) != c['bytes'] or hashlib.sha256(b).hexdigest() != c['sha256']:
                        raise ValueError('Partial chunk integrity failed')
                if offset != state['offset']:
                    raise ValueError('Invalid journal offset')
                if partial.stat().st_size > offset:
                    if shutil.disk_usage(destination.parent).free - (partial.stat().st_size - offset) - 2**20 < reserve:
                        raise OSError('Paused before preserving uncommitted tail: free-space reserve')
                    tail = partial.with_name(partial.name + f'.uncommitted-{time.time_ns()}')
                    with tail.open('xb') as out:
                        shutil.copyfileobj(f, out, 2**20)
                    with partial.open('r+b') as out:
                        out.truncate(offset)
        elif partial.exists():
            raise ValueError('Unjournaled source exists; preserved for inspection')
        if shutil.disk_usage(destination.parent).free - (source['bytes'] - state['offset']) - 2**20 < reserve:
            raise OSError('Paused before download: preserving free-space reserve')
        with open_request(source['url'], method='HEAD') as response:
            length = int(response.headers.get('Content-Length', 0))
            etag = response.headers.get('ETag')
        if length != source['bytes']:
            raise ValueError('Remote source length differs from registered archive')
        if state.get('etag') and state['etag'] != etag:
            raise ValueError('Remote ETag changed during resume')
        state['etag'] = etag
        if not partial.exists():
            partial.touch(exist_ok=False)
        atomic_json(journal, state, reserve)
        started = time.monotonic()
        try:
            # A completed partial can be hashed/published without another GET.
            if state['offset'] < source['bytes']:
                start = state['offset']; end = source['bytes'] - 1
                headers = {'Range': f'bytes={start}-{end}'}
                if etag: headers['If-Match'] = etag
                with open_request(source['url'], headers) as response:
                    if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{source["bytes"]}':
                        raise ValueError('Remote did not honor the exact registered interval')
                    with partial.open('ab') as out:
                        while state['offset'] < source['bytes']:
                            length = min(chunk_size, source['bytes'] - state['offset'])
                            h = hashlib.sha256(); received = 0
                            while received < length:
                                b = response.read(min(2**20, length - received))
                                if not b: raise OSError('Interrupted source response; complete chunks retained')
                                if shutil.disk_usage(destination.parent).free - len(b) - 2**20 < reserve:
                                    raise OSError('Paused at free-space reserve')
                                out.write(b); h.update(b); received += len(b)
                            out.flush(); os.fsync(out.fileno())
                            state['chunks'].append({'bytes': received, 'sha256': h.hexdigest()})
                            state['offset'] += received
                            atomic_json(journal, state, reserve)
                            if progress: progress(state['offset'], source['bytes'])
                        if response.read(1): raise ValueError('Response exceeds registered length')
            identity = hashes(partial)
            if identity['bytes'] != source['bytes'] or identity['md5'] != source['md5']:
                raise ValueError('Full source checksum mismatch; partial preserved')
            partial.rename(destination)
            state.update(status='complete', identity=identity, elapsed_seconds=time.monotonic()-started)
            atomic_json(journal, state, reserve)
            return identity | {'cached': False, 'download_seconds': state['elapsed_seconds']}
        except BaseException as exc:
            state.update(status='interrupted', error=f'{type(exc).__name__}: {exc}')
            try: atomic_json(journal, state, reserve)
            except OSError: pass
            raise

"""Failure/restart tests for scientifically pinned large archives."""
import hashlib
import io
import json
from types import SimpleNamespace

import pytest

from cns_audit import download as d


class Response(io.BytesIO):
    def __init__(self, body=b'', status=206, headers=None):
        super().__init__(body)
        self.status, self.headers = status, headers or {}


@pytest.fixture
def remote(monkeypatch):
    body = b'abcdefghijklmno'
    source = dict(url='https://example.invalid/pinned', bytes=len(body), md5=hashlib.md5(body).hexdigest())
    calls = []
    state = {'short': None, 'status': 206, 'etag': '"pinned"'}
    def request(url, headers=None, method='GET'):
        calls.append((method, headers))
        if method == 'HEAD':
            return Response(headers={'Content-Length': str(len(body)), 'ETag': state['etag']})
        start, end = map(int, headers['Range'][6:].split('-'))
        assert headers['If-Match'] == state['etag']
        data = body[start:end+1]
        if state['short'] is not None:
            data = data[:state['short']]
        return Response(data, state['status'], {'Content-Range': f'bytes {start}-{end}/{len(body)}'})
    monkeypatch.setattr(d, 'open_request', request)
    return source, body, calls, state


def test_verified_publication_and_cached_no_network(tmp_path, remote):
    source, body, calls, _ = remote
    result = d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert result['sha256'] == hashlib.sha256(body).hexdigest()
    assert (tmp_path/'raw').read_bytes() == body
    assert not (tmp_path/'raw.part').exists()
    assert len(json.loads((tmp_path/'raw.download.json').read_text())['chunks']) == 4
    count = len(calls)
    assert d.verified_download(source, tmp_path/'raw', reserve=0)['cached']
    assert len(calls) == count


def test_interruption_resume_preserves_uncommitted_bytes(tmp_path, remote):
    source, body, calls, state = remote
    state['short'] = 6
    with pytest.raises(OSError, match='Interrupted'):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert not (tmp_path/'raw').exists()
    assert (tmp_path/'raw.part').read_bytes() == body[:6]
    assert json.loads((tmp_path/'raw.download.json').read_text())['offset'] == 4
    state['short'] = None
    d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert list(tmp_path.glob('raw.part.uncommitted-*'))[0].read_bytes() == body[4:6]
    assert calls[-1][1]['Range'] == 'bytes=4-14'
    assert (tmp_path/'raw').read_bytes() == body


def test_corrupted_committed_chunk_stops_before_network(tmp_path, remote):
    source, _, calls, state = remote
    state['short'] = 5
    with pytest.raises(OSError):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    (tmp_path/'raw.part').write_bytes(b'corrupt')
    count = len(calls)
    with pytest.raises(ValueError, match='integrity'):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert len(calls) == count


@pytest.mark.parametrize('changed', ['bytes', 'md5', 'url'])
def test_changed_identity_cannot_resume(tmp_path, remote, changed):
    source, _, calls, state = remote
    state['short'] = 5
    with pytest.raises(OSError):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    altered = source | {changed: {'bytes': 99, 'md5': '0'*32, 'url': 'elsewhere'}[changed]}
    count = len(calls)
    with pytest.raises(ValueError, match='identity'):
        d.verified_download(altered, tmp_path/'raw', chunk_size=4, reserve=0)
    assert len(calls) == count


def test_range_rejection_is_resumable(tmp_path, remote):
    source, body, _, state = remote
    state['status'] = 200
    with pytest.raises(ValueError, match='interval'):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert (tmp_path/'raw.part').read_bytes() == b''
    state['status'] = 206
    d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    assert (tmp_path/'raw').read_bytes() == body


def test_wrong_checksum_never_published(tmp_path, remote):
    source, body, _, _ = remote
    with pytest.raises(ValueError, match='checksum'):
        d.verified_download(source | {'md5': '0'*32}, tmp_path/'raw', reserve=0)
    assert not (tmp_path/'raw').exists()
    assert (tmp_path/'raw.part').read_bytes() == body


def test_low_space_no_network(tmp_path, remote, monkeypatch):
    source, _, calls, _ = remote
    monkeypatch.setattr(d.shutil, 'disk_usage', lambda _: SimpleNamespace(free=d.RESERVE + 2**20))
    with pytest.raises(OSError, match='reserve'):
        d.verified_download(source, tmp_path/'raw')
    assert not calls


def test_preserve_existing_mismatch(tmp_path, remote):
    source, _, calls, _ = remote
    (tmp_path/'raw').write_bytes(b'evidence')
    with pytest.raises(ValueError, match='preserved'):
        d.verified_download(source, tmp_path/'raw', reserve=0)
    assert (tmp_path/'raw').read_bytes() == b'evidence'
    assert not calls


def test_changed_etag_resume_stops(tmp_path, remote):
    source, _, _, state = remote
    state['short'] = 5
    with pytest.raises(OSError):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)
    state.update(short=None, etag='"different"')
    with pytest.raises(ValueError, match='ETag'):
        d.verified_download(source, tmp_path/'raw', chunk_size=4, reserve=0)

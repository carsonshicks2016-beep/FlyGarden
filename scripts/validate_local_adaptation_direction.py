"""Frozen 28-trial directional/gradient validation of the local-only candidate."""
import argparse
import fcntl
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT));sys.path.insert(0, str(ROOT / 'scripts'))
import sweep_adaptive_lif as reference
from flygarden.continuous_candidate import file_sha
from flygarden.directional_metrics import evaluate_traces
from flygarden.recording import atomic_json, space_check

BASE = ROOT / 'reports/brain-integration/recovery'
OUT = BASE / 'local-adaptation-direction-v1'
SEEDS = [12301, 12302]
CUES = ['none', 'a_left', 'a_right', 'a_both', 'equal', 'g60', 'g40']
RATE_KEYS = ['DM1_lPN_left', 'DM1_lPN_right', 'DNa02_left', 'DNa02_right', 'DNp09_left', 'DNp09_right']


def prepare():
    assert not OUT.exists(), 'Preserve existing protocol/evidence; resume without --prepare'
    parent_path = BASE / 'local-adaptation-closed-loop-v1/protocol.json'
    parent = json.loads(parent_path.read_text())
    assert all(file_sha(ROOT / name) == sha for name, sha in parent['sources'].items())
    sources = {**parent['sources']}
    for name in ['scripts/validate_local_adaptation_direction.py', 'flygarden/directional_metrics.py',
                 'tests/test_directional_metrics.py', 'scripts/audit_local_direction.py',
                 'scripts/plot_local_direction.py', str(parent_path.relative_to(ROOT)),
                 'reports/brain-integration/recovery/local-adaptation-closed-loop-v1/results.json']:
        sources[name] = file_sha(ROOT / name)
    protocol_files = subprocess.check_output(['rg', '--files', '--hidden', '-g', '*protocol*.json',
                                             'reports/brain-integration'], cwd=ROOT).decode().splitlines()
    used = set()
    def integers(value):
        if isinstance(value, int):used.add(value)
        elif isinstance(value, list):
            for item in value:integers(item)
        elif isinstance(value, dict):
            for item in value.values():integers(item)
    def visit(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if 'seed' in key.lower():integers(item)
                visit(item)
        elif isinstance(value, list):
            for item in value:visit(item)
    for file in protocol_files:visit(json.loads((ROOT / file).read_text()))
    assert not set(SEEDS) & used, 'Validation seeds previously registered'
    gates = {**parent['gates'], 'gradient_contrast_hz': 5,
             'motor_direction_contrast_hz': 10, 'motor_gradient_contrast_hz': 5}
    protocol = {key: parent[key] for key in ['mapping', 'selected', 'selected_local_targets',
                                             'pulse_windows', 'recovery_windows', 'burst_windows',
                                             'models', 'domains', 'parameters', 'mechanism_isolation']}
    protocol.update(version=1, registered_before_execution=True, registered_unix=time.time(),
                    validation_seeds=SEEDS, cues=CUES, gates=gates, sources=sources,
                    trials=28, simulated_seconds_per_trial=6,
                    design='Frozen candidate vs original; two fresh validation seeds; seven cues; no sweep, fitting, gain/sign/decoder change or learning.',
                    sensory_cases={'none': [0, 0], 'a_left': [1, 0], 'a_right': [0, 1],
                                   'a_both': [1, 1], 'equal': [.5, .5], 'g60': [.6, .4], 'g40': [.4, .6]},
                    input='Original50Hz maximum per ORN,65Hz per DNp09 support; odorA only. Equal/g60/g40 keep total concentration1. a_both is the separate full-intensity bilateral condition.',
                    primary_gate3='For every seed/pulse: PN left-minus-right contrast(a_left)-contrast(a_right)>=10Hz; a_left>none and a_right<none. Exactly the previous multi-trial evaluator; no fitted baseline subtraction.',
                    primary_gate6='For every seed/pulse: PN contrast(g60)-contrast(g40)>=5Hz; g60>equal and g40<equal. Exactly the existing unexecuted gradient evaluator.',
                    uncertainty='Require every seed/pulse. Report all values/signs; two seeds give a bounded repeatability screen, not population confidence or biological fidelity. No post-hoc threshold relaxation.',
                    additional_motor_alignment='Prospectively report separately: same bracketing rules on signed DNa02 outputs, minimum10Hz unilateral and5Hz gradient. These added interface checks cannot replace failed original PN gates.',
                    continuation='Four left-cue trials: checkpoint at3.775s; fresh-process next5 windows exact events/inputs/motor; whole v/g/adapt error<=1e-10mV.',
                    interruption='Preserve complete chunks. Reconstruct a partial trial from its fixed seed and verify every existing chunk before appending; never delete or silently overwrite recorded evidence.',
                    interruption_validation='Terminate the owned candidate-a_right-12301 worker after at least60 complete windows and before trial completion; retain/hash its completed prefix, reconstruct from the same seed, compare every existing chunk exactly and finish. No stimulus or parameter change.',
                    scheduling={'workers': 1, 'reason': 'Memory-bound Mac session; use fresh measured telemetry. No concurrent simulation or export workers.'},
                    scope='Full-network engineering neural screen only. Local-cell physiology remains unqualified; no body, navigation, learning, odorB or long-duration qualification.',
                    promotion=False, seed_reservations_checked={'protocols': len(protocol_files), 'previous_seed_count': len(used)})
    space_check(ROOT, 2 * 1024 ** 3)
    OUT.mkdir();atomic_json(OUT / 'protocol.json', protocol)
    atomic_json(OUT / 'progress.json', {'status': 'prepared', 'planned_trials': 28, 'completed': [], 'promoted': False})
    print('Registered28 trials on fresh seeds12301/12302; all mechanisms and gates frozen.', flush=True)


def verify():
    protocol = json.loads((OUT / 'protocol.json').read_text())
    assert all(file_sha(ROOT / name) == sha for name, sha in protocol['sources'].items()), 'Pinned source changed'
    return protocol


def worker(model, cue, seed, continuation=False):
    p = verify();assert model in p['models'] and cue in p['cues'] and seed in p['validation_seeds']
    folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
    started = time.monotonic();candidate = reference.construct(p, model, seed)
    assert candidate.brain.n == 138639 and candidate.brain.edges == 15091983
    if continuation:
        candidate.load(folder / 'checkpoint')
        for tick in range(151, 156):
            data = reference.arrays(candidate, p, reference.advance(candidate, cue, tick))
            with np.load(folder / f'window-{tick:04d}.npz') as z:
                assert set(z.files) == set(data) and all(np.array_equal(z[k], v) for k, v in data.items())
        with np.load(folder / 'continuation-state.npz') as z:
            errors = {k: float(np.max(abs(v - z[k]))) for k, v in reference.fullstate(candidate).items()}
        assert max(errors.values()) <= p['gates']['state_precision_mV']
        atomic_json(folder / 'continuation-result.json', {'status': 'passed', 'fresh_process': True,
                                                        'windows': 5, 'errors_mV': errors})
        return
    weight = hashlib.sha256(np.asarray(candidate.brain.synapses.w[:]).tobytes()).hexdigest()
    if (folder / 'manifest.json').exists():
        manifest = json.loads((folder / 'manifest.json').read_text())
        rows = json.loads((folder / 'rows.json').read_text())
        assert manifest['sources'] == p['sources'] and manifest['initial_weight_hash'] == weight
        existing = len(manifest['chunks']);assert existing <= 240
        assert len(rows) in (existing, existing + 1), 'Unexpected recording metadata interruption'
        orphan_row = rows[existing] if len(rows) > existing else None
        rows = rows[:existing]
    else:
        folder.mkdir(parents=True, exist_ok=False)
        manifest = {'status': 'running', 'model': model, 'case': cue, 'seed': seed, 'controller': candidate.manifest(),
                    'protocol_sha256': file_sha(OUT / 'protocol.json'), 'sources': p['sources'],
                    'initial_weight_hash': weight, 'chunks': []}
        rows = [];existing = 0;orphan_row = None
        atomic_json(folder / 'manifest.json', manifest);atomic_json(folder / 'rows.json', rows)
    try:
        for tick in range(240):
            data = reference.arrays(candidate, p, reference.advance(candidate, cue, tick))
            assert all(np.isfinite(v).all() for v in data.values())
            assert np.array_equal(np.bincount(data['spike_i'], minlength=138639), data['counts'])
            file = folder / f'window-{tick:04d}.npz'
            if file.exists():
                with np.load(file) as z:
                    assert set(z.files) == set(data) and all(np.array_equal(z[k], v) for k, v in data.items()), ('Existing chunk differs', file)
                if tick < existing:assert file_sha(file) == manifest['chunks'][tick]['sha256']
            else:
                assert tick >= existing, 'Missing complete chunk'
                space_check(folder, 8 * 1024 ** 2)
                with file.with_suffix('.tmp').open('wb') as stream:np.savez_compressed(stream, **data)
                file.with_suffix('.tmp').replace(file)
            if tick >= existing:
                manifest['chunks'].append({'file': file.name, 'sha256': file_sha(file), 'end': candidate.time})
                row = {'end': candidate.time, 'population_hz': candidate.last['population_hz'],
                       'requested_hz': candidate.last['requested_hz'], 'motor': data['motor'].tolist()}
                if tick == existing and orphan_row is not None:assert row == orphan_row
                rows.append(row)
                atomic_json(folder / 'rows.json', rows);atomic_json(folder / 'manifest.json', manifest)
            atomic_json(OUT / 'current-worker.json', {'trial': folder.name, 'pid': os.getpid(),
                        'completed_windows': tick + 1, 'planned_windows': 240, 'simulated_seconds': candidate.time,
                        'wall_seconds': time.monotonic() - started, 'rss_bytes': psutil.Process().memory_info().rss,
                        'swap_used_bytes': psutil.swap_memory().used})
            if cue == 'a_left' and tick == 150 and not (folder / 'checkpoint').exists():
                staging = folder / f'checkpoint-staging-{time.time_ns()}'
                candidate.save(staging);staging.replace(folder / 'checkpoint')
            if cue == 'a_left' and tick == 155:
                state = reference.fullstate(candidate);target = folder / 'continuation-state.npz'
                if target.exists():
                    with np.load(target) as z:assert all(np.array_equal(z[k], v) for k, v in state.items())
                else:
                    with target.with_suffix('.tmp').open('wb') as stream:np.savez_compressed(stream, **state)
                    target.with_suffix('.tmp').replace(target)
        final = hashlib.sha256(np.asarray(candidate.brain.synapses.w[:]).tobytes()).hexdigest()
        assert final == weight and candidate.brain.plasticity.updates == 0
        verify();manifest.update(status='complete', final_weight_hash=final, learning_updates=0,
                                reconstructed_windows=existing, wall_seconds=time.monotonic() - started,
                                peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        atomic_json(folder / 'manifest.json', manifest)
        print(folder.name, 'complete', round(manifest['wall_seconds'], 1), 'seconds', flush=True)
    except BaseException as error:
        manifest.update(status='interrupted', error=repr(error));atomic_json(folder / 'manifest.json', manifest);raise


def evaluate(p):
    traces = {};inputs = {};chunks = 0
    for model in p['models']:
        for seed in p['validation_seeds']:
            for cue in p['cues']:
                folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
                m = json.loads((folder / 'manifest.json').read_text());rows = json.loads((folder / 'rows.json').read_text())
                assert m['status'] == 'complete' and len(m['chunks']) == len(rows) == 240
                assert m['initial_weight_hash'] == m['final_weight_hash'] and m['learning_updates'] == 0
                local = []
                for ch in m['chunks']:
                    file = folder / ch['file'];assert file_sha(file) == ch['sha256']
                    with np.load(file) as z:
                        assert np.array_equal(np.bincount(z['spike_i'], minlength=138639), z['counts'])
                        local.append(z['counts'][[x['index'] for x in p['selected_local_targets']]] / .025)
                        digest = hashlib.sha256(z['external_i'].tobytes() + z['external_t'].tobytes()).hexdigest()
                        key = (seed, cue, ch['file'])
                        if key in inputs:assert digest == inputs[key]
                        else:inputs[key] = digest
                    chunks += 1
                traces[(model, seed, cue)] = np.column_stack([np.array([[r['population_hz'][k] for k in RATE_KEYS] for r in rows]), np.array(local)])
    result = evaluate_traces(p, traces)
    result.update(chunks_audited=chunks, paired_external_inputs_exact=True,
                  protocol_sha256=file_sha(OUT / 'protocol.json'))
    return result


def interrupt_reference(model, cue, seed):
    """One controlled stop of our own worker; never target another process."""
    receipt_path = OUT / 'interruption-test.json'
    if receipt_path.exists():return
    folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
    if (folder / 'manifest.json').exists():
        raise RuntimeError('Interruption receipt missing for an existing target; inspect evidence before resuming')
    process = subprocess.Popen([sys.executable, '-B', __file__, '--worker', '--model', model,
                                '--cue', cue, '--seed', str(seed)], cwd=ROOT)
    deadline = time.monotonic() + 180
    try:
        while process.poll() is None and time.monotonic() < deadline:
            current_path = OUT / 'current-worker.json'
            if current_path.exists():
                current = json.loads(current_path.read_text())
                if current['pid'] == process.pid and current['completed_windows'] >= 60:
                    process.terminate();code = process.wait(timeout=20)
                    manifest = json.loads((folder / 'manifest.json').read_text())
                    assert 60 <= len(manifest['chunks']) < 240 and code != 0
                    atomic_json(receipt_path, {'trial': folder.name, 'owned_worker_pid': process.pid,
                                              'controlled_termination': True, 'return_code': code,
                                              'complete_prefix': manifest['chunks'], 'status': 'prefix_preserved_pending_reconstruction'})
                    print('Controlled interruption: preserved', len(manifest['chunks']), 'chunks.', flush=True)
                    return
            time.sleep(.1)
        raise RuntimeError('Owned worker did not reach the interruption point')
    finally:
        if process.poll() is None:process.terminate();process.wait(timeout=20)


def run():
    p = verify();done = [];samples = [];started = time.monotonic()
    with (ROOT / '.runtime/experiment.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for seed in p['validation_seeds']:
            for model in p['models']:
                for cue in p['cues']:
                    name = f'{model}-{cue}-{seed}';folder = OUT / 'trials' / name
                    atomic_json(OUT / 'progress.json', {'status': 'running', 'completed': done, 'planned_trials': 28,
                                'current': name, 'pid': os.getpid(), 'workers': 1, 'promoted': False})
                    finished = (folder / 'manifest.json').exists() and json.loads((folder / 'manifest.json').read_text())['status'] == 'complete'
                    if not finished:
                        space_check(OUT, 1200 * 1024 ** 2)
                        if (model, cue, seed) == ('local_adaptive', 'a_right', SEEDS[0]):interrupt_reference(model, cue, seed)
                        subprocess.run([sys.executable, '-B', __file__, '--worker', '--model', model,
                                        '--cue', cue, '--seed', str(seed)], cwd=ROOT, check=True)
                    if cue == 'a_left' and not (folder / 'continuation-result.json').exists():
                        subprocess.run([sys.executable, '-B', __file__, '--worker', '--model', model,
                                        '--cue', cue, '--seed', str(seed), '--continuation'], cwd=ROOT, check=True)
                    done.append(name);swap = psutil.swap_memory()
                    samples.append({'trial': name, 'swap_used_bytes': swap.used, 'swap_out_bytes': swap.sout,
                                    'available_memory_bytes': psutil.virtual_memory().available})
        result = evaluate(p);result.update(trials=28, wall_seconds=time.monotonic() - started, scheduling_samples=samples)
        atomic_json(OUT / 'results.json', result)
        atomic_json(OUT / 'progress.json', {'status': 'complete', 'completed': done, 'planned_trials': 28,
                                          'workers': 1, 'promoted': False})
        print('Directional/gradient validation complete; no controller promotion.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--worker', action='store_true');parser.add_argument('--continuation', action='store_true')
    parser.add_argument('--model');parser.add_argument('--cue');parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    if args.prepare:prepare()
    elif args.worker:worker(args.model, args.cue, args.seed, args.continuation)
    else:
        try:run()
        except BaseException as error:
            atomic_json(OUT / 'progress.json', {'status': 'interrupted', 'error': repr(error), 'promoted': False});raise

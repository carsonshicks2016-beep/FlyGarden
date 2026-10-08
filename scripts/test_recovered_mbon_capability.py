"""Eight preregistered full-network direct-MBON32 capability trials."""
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
import pandas as pd
import psutil

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.mbon_capability import CASES, PULSES, RECOVERY, evaluate_capability
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
OUT = BASE/'recovered-mbon32-capability-v1'
PARENT = BASE/'local-adaptation-direction-v1'
SEEDS = [12401, 12402]
RATE_KEYS = ['MBON32_left', 'MBON32_right', 'DNa02_left', 'DNa02_right',
             'DNp09_left', 'DNp09_right', 'DM1_lPN_left', 'DM1_lPN_right']


def prepare():
    if OUT.exists(): raise FileExistsError('Preserve existing protocol; resume without --prepare')
    parent = json.loads((PARENT/'protocol.json').read_text())
    assert all(file_sha(ROOT/name) == value for name, value in parent['sources'].items())
    ids = pd.read_csv(ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv', index_col=0).index.astype(str)
    ann = pd.read_csv(ROOT/'data/annotations.tsv', sep='\t', dtype={'root_id': str}, low_memory=False).fillna('')
    targets = []; roots = []; mapping = dict(parent['mapping'])
    for side in ['left', 'right']:
        rows = ann[ann.cell_type.eq('MBON32') & ann.side.eq(side) & ann.root_id.isin(ids)]
        assert len(rows) == 1
        root = rows.iloc[0].root_id; index = int(np.flatnonzero(ids == root)[0])
        roots.append(root); targets.append(index)
        mapping['MBON32_'+side] = [dict(root_id=root, index=index, cell_type='MBON32', side=side)]
    historical = json.loads((BASE/'mbon32-capability-v1/protocol.json').read_text())
    assert targets == historical['targets'] and roots == historical['roots']
    receiver = json.loads((BASE/'receiver-counterfactual-v1/protocol.json').read_text())
    aotu_targets = []
    for node in receiver['aotu_sources']:
        assert ids[node['index']] == node['root_id']
        row = ann[ann.root_id.eq(node['root_id'])]
        assert len(row) == 1 and row.iloc[0].cell_type == 'AOTU019' and row.iloc[0].known_nt == 'gaba'
        aotu_targets.append(node['index'])
    used = set()
    def integers(v):
        if isinstance(v, int): used.add(v)
        elif isinstance(v, list):
            for item in v: integers(item)
        elif isinstance(v, dict):
            for item in v.values(): integers(item)
    def scan(v):
        if isinstance(v, dict):
            for key, item in v.items():
                if 'seed' in key.lower(): integers(item)
                scan(item)
        elif isinstance(v, list):
            for item in v: scan(item)
    files = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*protocol*.json',
                                     'reports/brain-integration'], cwd=ROOT).decode().splitlines()
    for path in files: scan(json.loads((ROOT/path).read_text()))
    assert not set(SEEDS) & used, 'Diagnostic seeds already reserved'
    sources = dict(parent['sources'])
    paths = ['scripts/test_recovered_mbon_capability.py', 'scripts/audit_recovered_mbon_capability.py',
             'scripts/plot_recovered_mbon_capability.py', 'flygarden/mbon_capability.py',
             'flygarden/mbon_capability_candidate.py', 'tests/test_mbon_capability.py', 'flygarden/neural_probe.py',
             'scripts/sweep_adaptive_lif.py', str((PARENT/'protocol.json').relative_to(ROOT)),
             str((PARENT/'results.json').relative_to(ROOT)), str((PARENT/'independent-audit.json').relative_to(ROOT)),
             'reports/brain-integration/recovery/mbon32-capability-v1/protocol.json',
             'reports/brain-integration/recovery/mbon32-capability-v1/results.json',
             'reports/brain-integration/recovery/receiver-counterfactual-v1/protocol.json',
             'reports/brain-integration/recovery/receiver-counterfactual-v1/results.json',
             'reports/brain-integration/recovery/receiver-counterfactual-v1/independent-audit.json']
    sources.update({name: file_sha(ROOT/name) for name in paths})
    p = dict(version=1, registered_before_execution=True, registered_unix=time.time(), sources=sources,
        question='Can fixed direct left/right MBON32 input produce opposed descending outputs and renewed response in the recovered intact recurrent network?',
        scope='Engineering downstream capability screen. No odor, vision, body, acquisition, gradient qualification, fitted decoder or controller promotion.',
        diagnostic_seeds=SEEDS, seed_reservations_checked=dict(protocols=len(files), previous_seed_values=len(used)),
        cases=list(CASES), trials=8, model='local_adaptive', mapping=mapping, direct_targets=targets, direct_roots=roots,
        domain=parent['domains']['local_adaptive'], parameters=parent['parameters']['local_adaptive'],
        selected=sorted(set(parent['selected']+targets+aotu_targets)), selected_local_targets=parent['selected_local_targets'],
        interval_s=.025, neural_clock_s=.0001, duration_s=6, windows=240,
        pulse_windows=list(PULSES), recovery_windows=list(RECOVERY), burst_windows=parent['burst_windows'],
        input=dict(support_hz=65, MBON32_hz=50, jump_mV=68.75, direct_rng_seed_offset=100000,
                   odor_hz=0, visual_hz=0, all_possible_candidate_inputs_zero_refractory=True,
                   additional_zero_refractory_indices=targets,
                   deviation='Two MBON32 roots are additionally zero refractory in all cases, including none. Matches historical direct-drive convention; differs from odor-only candidate operating state.'),
        preservation='Full138639-neuron/15091983-record/54492922-site graph, signs, weights, local-only395-cell adaptation(.45s/13.5mV), support and descending decoder remain fixed; plasticity disabled.',
        gates=dict(historical_direct_capability_per_side_delta_hz=5, bilateral_delta_bound_hz=5,
                   existing_descending_separation_hz=10, response_gain_hz=10, individual_recovery_bound_hz=5,
                   signed_DNa02_recovery_bound_hz=5, late_100ms_excess_bound_hz=20,
                   matched_candidate_support_retention_fraction=.8, state_precision_mV=1e-10),
        measurements=dict(direction='For every seed/pulse: left-minus-none>=5Hz; right-minus-none<=-5Hz; bilateral delta within5Hz; separately retain existing10Hz separation and bracketing rule on DNa02.',
            response='Each stimulated MBON at each pulse gains>=10Hz versus matched none. Second pulse also gains>=10Hz over its own first recovery.',
            recovery='Each MBON, each PN and four selected locals differ from matched none by<=5Hz; signed DNa02 difference<=5Hz in[100,120) and[220,240).',
            bursts='Late windows retain PN100ms excess<=20Hz; additionally named MBON each-side100ms excess<=20Hz.',
            support='Each stimulated case/pulse and recovery retains>=.8 of strictly positive matched candidate-none per-side DNp09 activity. This is a new perturbation diagnostic, not the previous candidate-vs-original support qualification.',
            originals='Original PN Gate3/6 failures preserved; this direct-input screen does not retest or replace them. Historical original-model MBON failure is not a matched fresh control.'),
        continuation='Both left cases checkpoint after window150 at3.775s. Fresh processes reproduce next5 chunks, full-network v/g/adapt within1e-10mV, direct/support events and decoder state.',
        interruption='One owned right-first-seed worker terminated after>=60 complete chunks; preserve/hash prefix, reconstruct from fixed seed and exactly compare all existing chunks before appending. All other interrupted attempts also reconstruct without deletion.',
        scheduling=dict(workers=1, reason='4GiB available/4GiB preexisting swap; prior candidate process2.0-2.6GiB. Avoid concurrent full-network/export workers.',
                        baseline_available_bytes=psutil.virtual_memory().available, baseline_swap_bytes=psutil.swap_memory().used),
        recording='All neuron spikes/counts, support/direct requested and generator-delivered events, decoder commands, 26 selected endpoint states; bounded compressed immutable chunks. No video/body pose in this neural screen.',
        uncertainty='Two fresh diagnostic seeds and repeated pulses; bounded repeatability, not a confidence interval or biological validation.',
        promotion=False, acceptance_criteria_changed=False)
    assert len(p['domain']['indices']) == 395 and p['parameters'] == {'tau_s': .45, 'step_mv': 13.5}
    space_check(ROOT, 1200*1024**2); OUT.mkdir()
    atomic_json(OUT/'protocol.json', p); atomic_json(OUT/'progress.json', dict(status='prepared', planned_trials=8, completed=[], promoted=False))
    print('Registered eight intact-network trials on fresh diagnostic seeds12401/12402.', flush=True)


def verify():
    p = json.loads((OUT/'protocol.json').read_text())
    assert all(file_sha(ROOT/name) == value for name, value in p['sources'].items()), 'Pinned source changed'
    return p


def arrays(candidate, p, motor):
    from scripts.sweep_adaptive_lif import arrays as base_arrays
    data = base_arrays(candidate, p, motor)
    data.update({k: candidate.last[k] for k in ['mbon_i', 'mbon_t', 'mbon_delivered_i', 'mbon_delivered_t']})
    return data


def publish_arrays(path, data):
    space_check(path.parent, sum(x.nbytes for x in data.values())+1024**2)
    temporary = path.with_name(path.name+'.tmp-'+str(time.time_ns()))
    with temporary.open('wb') as stream:
        np.savez_compressed(stream, **data); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def worker(case, seed, continuation=False):
    from flygarden.mbon_capability_candidate import MBONCapabilityCandidate
    from scripts.sweep_adaptive_lif import fullstate
    p = verify(); assert case in CASES and seed in SEEDS
    folder = OUT/'trials'/f'{case}-{seed}'; started = time.monotonic()
    c = MBONCapabilityCandidate(p['mapping'], p['domain'], p['direct_targets'], seed)
    assert (c.brain.n, c.brain.edges, c.brain.anatomical_synapses) == (138639, 15091983, 54492922)
    if continuation:
        c.load(folder/'checkpoint')
        for tick in range(151, 156):
            data = arrays(c, p, c.advance_capability(case, tick))
            with np.load(folder/f'window-{tick:04d}.npz') as z:
                assert set(z.files) == set(data) and all(np.array_equal(z[k], v) for k, v in data.items())
        with np.load(folder/'continuation-state.npz') as z:
            errors = {k: float(np.max(abs(v-z[k]))) for k, v in fullstate(c).items()}
        assert max(errors.values()) <= p['gates']['state_precision_mV']
        atomic_json(folder/'continuation-result.json', dict(status='passed', fresh_process=True, windows=5,
                    errors_mV=errors, checkpoint_integrity_sha256=file_sha(folder/'checkpoint/integrity.json')))
        print('Fresh-process continuation passed', folder.name, errors, flush=True); return
    weight = hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest()
    assert weight == 'f6f6ab9f7c49e14a906d120c705e6af7814ecdeeecaaefad8b1280bdb71e7732'
    if (folder/'manifest.json').exists():
        m = json.loads((folder/'manifest.json').read_text()); rows = json.loads((folder/'rows.json').read_text())
        assert m['sources'] == p['sources'] and m['initial_weight_hash'] == weight and m['controller'] == c.manifest()
        existing = len(m['chunks']); assert existing <= 240 and len(rows) in (existing, existing+1)
        orphan = rows[existing] if len(rows) > existing else None; rows = rows[:existing]
    else:
        folder.mkdir(parents=True, exist_ok=False); existing = 0; orphan = None; rows = []
        m = dict(status='running', case=case, seed=seed, model='local_adaptive', controller=c.manifest(),
                 sources=p['sources'], protocol_sha256=file_sha(OUT/'protocol.json'), initial_weight_hash=weight, chunks=[])
        atomic_json(folder/'manifest.json', m); atomic_json(folder/'rows.json', rows)
    try:
        for tick in range(240):
            data = arrays(c, p, c.advance_capability(case, tick))
            assert all(np.isfinite(v).all() for v in data.values())
            np.testing.assert_array_equal(np.bincount(data['spike_i'], minlength=138639), data['counts'])
            path = folder/f'window-{tick:04d}.npz'
            if path.exists():
                with np.load(path) as z: assert set(z.files) == set(data) and all(np.array_equal(z[k], v) for k, v in data.items()), path
                if tick < existing: assert file_sha(path) == m['chunks'][tick]['sha256']
            else:
                assert tick >= existing; publish_arrays(path, data)
            if tick >= existing:
                row = dict(end=c.time, population_hz=c.last['population_hz'], requested_hz=c.last['requested_hz'], motor=data['motor'].tolist())
                if tick == existing and orphan is not None: assert row == orphan
                rows.append(row); m['chunks'].append(dict(file=path.name, sha256=file_sha(path), end=c.time))
                atomic_json(folder/'rows.json', rows); atomic_json(folder/'manifest.json', m)
            atomic_json(OUT/'current-worker.json', dict(trial=folder.name, pid=os.getpid(), completed_windows=tick+1,
                reconstructed_prefix_windows=min(tick+1, existing), simulated_seconds=c.time, wall_seconds=time.monotonic()-started,
                rss_bytes=psutil.Process().memory_info().rss, swap_used_bytes=psutil.swap_memory().used))
            if case == 'left' and tick == 150 and not (folder/'checkpoint').exists():
                staging = folder/('checkpoint-staging-'+str(time.time_ns())); c.save(staging); staging.replace(folder/'checkpoint')
            if case == 'left' and tick == 155:
                path = folder/'continuation-state.npz'; state = fullstate(c)
                if path.exists():
                    with np.load(path) as z: assert all(np.array_equal(z[k], v) for k, v in state.items())
                else: publish_arrays(path, state)
        final = hashlib.sha256(np.asarray(c.brain.synapses.w[:]).tobytes()).hexdigest()
        assert final == weight and c.brain.plasticity.updates == 0
        verify(); m.update(status='complete', final_weight_hash=final, learning_updates=0, reconstructed_windows=existing,
                           wall_seconds=time.monotonic()-started, peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        atomic_json(folder/'manifest.json', m)
        print(folder.name, 'complete', round(m['wall_seconds'], 1), 'seconds', flush=True)
    except BaseException as error:
        m.update(status='interrupted', error=repr(error)); atomic_json(folder/'manifest.json', m); raise


def evaluate(p):
    traces = {}; chunks = 0
    locals_ = [x['index'] for x in p['selected_local_targets']]
    for seed in SEEDS:
        for case in CASES:
            folder = OUT/'trials'/f'{case}-{seed}'; m = json.loads((folder/'manifest.json').read_text())
            assert m['status'] == 'complete' and len(m['chunks']) == 240 and m['initial_weight_hash'] == m['final_weight_hash']
            rows = []
            for ch in m['chunks']:
                path = folder/ch['file']; assert file_sha(path) == ch['sha256']
                with np.load(path) as z:
                    counts = np.bincount(z['spike_i'], minlength=138639); np.testing.assert_array_equal(counts, z['counts'])
                    rows.append([float(counts[[n['index'] for n in p['mapping'][key]]].mean()/.025) for key in RATE_KEYS]+
                                (counts[locals_]/.025).tolist())
                chunks += 1
            traces[seed, case] = np.asarray(rows)
    r = evaluate_capability(p, traces)
    r.update(protocol_sha256=file_sha(OUT/'protocol.json'), chunks_audited=chunks, trials=8,
             continuation_checks=[json.loads((OUT/'trials'/f'left-{seed}'/'continuation-result.json').read_text()) for seed in SEEDS])
    return r


def controlled_interrupt(case, seed):
    receipt = OUT/'interruption-test.json'; folder = OUT/'trials'/f'{case}-{seed}'
    if receipt.exists(): return
    if folder.exists(): raise RuntimeError('Interruption target exists without receipt; preserve and inspect')
    process = subprocess.Popen([sys.executable, '-B', __file__, '--worker', '--case', case, '--seed', str(seed)], cwd=ROOT)
    try:
        deadline = time.monotonic()+240
        while process.poll() is None and time.monotonic() < deadline:
            path = OUT/'current-worker.json'
            if path.exists():
                current = json.loads(path.read_text())
                if current['pid'] == process.pid and current['completed_windows'] >= 60:
                    process.terminate(); code = process.wait(timeout=30)
                    m = json.loads((folder/'manifest.json').read_text()); assert 60 <= len(m['chunks']) < 240 and code != 0
                    m.update(status='interrupted', error='Controlled owned-worker termination for exact-prefix reconstruction')
                    atomic_json(folder/'manifest.json', m)
                    atomic_json(receipt, dict(trial=folder.name, owned_worker_pid=process.pid, return_code=code,
                        complete_prefix=m['chunks'], controlled_termination=True, status='prefix_preserved_pending_reconstruction'))
                    print('Owned-worker interruption preserved', len(m['chunks']), 'chunks', flush=True); return
            time.sleep(.1)
        raise RuntimeError('Interruption point not reached')
    finally:
        if process.poll() is None: process.terminate(); process.wait(timeout=30)


def run():
    p = verify(); started = time.monotonic(); completed = []; samples = []
    (ROOT/'.runtime').mkdir(exist_ok=True)
    with (ROOT/'.runtime/experiment.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for seed in SEEDS:
            for case in CASES:
                name = f'{case}-{seed}'; folder = OUT/'trials'/name
                atomic_json(OUT/'progress.json', dict(status='running', completed=completed, current=name,
                            planned_trials=8, pid=os.getpid(), workers=1, promoted=False))
                finished = (folder/'manifest.json').exists() and json.loads((folder/'manifest.json').read_text())['status'] == 'complete'
                if not finished:
                    space_check(OUT, 1200*1024**2)
                    if (case, seed) == ('right', SEEDS[0]): controlled_interrupt(case, seed)
                    subprocess.run([sys.executable, '-B', __file__, '--worker', '--case', case, '--seed', str(seed)], cwd=ROOT, check=True)
                if case == 'left' and not (folder/'continuation-result.json').exists():
                    subprocess.run([sys.executable, '-B', __file__, '--worker', '--case', case, '--seed', str(seed), '--continuation'], cwd=ROOT, check=True)
                completed.append(name); samples.append(dict(trial=name, swap_used_bytes=psutil.swap_memory().used,
                                    swap_out_bytes=psutil.swap_memory().sout, available_memory_bytes=psutil.virtual_memory().available))
        interrupted = json.loads((OUT/'interruption-test.json').read_text())
        m = json.loads((OUT/'trials'/interrupted['trial']/'manifest.json').read_text())
        assert m['reconstructed_windows'] >= len(interrupted['complete_prefix'])
        assert m['chunks'][:len(interrupted['complete_prefix'])] == interrupted['complete_prefix']
        interrupted.update(status='passed', prefix_reconstructed_exactly=True); atomic_json(OUT/'interruption-test.json', interrupted)
        result = evaluate(p); result.update(wall_seconds=time.monotonic()-started, scheduling_samples=samples)
        atomic_json(OUT/'results.json', result)
        subprocess.run([sys.executable, '-B', str(ROOT/'scripts/audit_recovered_mbon_capability.py')], cwd=ROOT, check=True)
        subprocess.run([sys.executable, '-B', str(ROOT/'scripts/plot_recovered_mbon_capability.py')], cwd=ROOT, check=True)
        atomic_json(OUT/'progress.json', dict(status='complete', completed=completed, planned_trials=8, workers=1, promoted=False))
        print('Eight-trial capability comparison and independent audit complete; no promotion.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--worker', action='store_true'); parser.add_argument('--continuation', action='store_true')
    parser.add_argument('--case', choices=CASES); parser.add_argument('--seed', type=int)
    args = parser.parse_args()
    if args.prepare: prepare()
    elif args.worker: worker(args.case, args.seed, args.continuation)
    else:
        try: run()
        except BaseException as error:
            atomic_json(OUT/'progress.json', dict(status='interrupted', error=repr(error), promoted=False)); raise

"""Trace completed adaptation trials without launching a neural simulation."""
import json, resource, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.feedback_trace import delayed_impulses, refractory_gate
from flygarden.recorded_drive import replay_recorded_states
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
PRIOR = BASE/'adaptive-parameter-sweep-v1'
OUT = BASE/'adaptive-feedback-trace-v1'
MODELS = ['original', 'projection_t450_b13p5', 'sensory_projection_t450_b13p5']
CUES = ['none', 'a_left', 'a_right', 'a_both']
SEEDS = [12001, 12002]
PHASES = {'pulse_1': [3000, 8000], 'recovery_1': [25000, 30000],
          'pulse_2': [33000, 38000], 'recovery_2': [55000, 60000]}


def load_trial(folder, columns, targets):
    m = json.loads((folder/'manifest.json').read_text())
    assert m['status'] == 'complete' and len(m['chunks']) == 240
    assert m['initial_weight_hash'] == m['final_weight_hash']
    indices = []; ticks = []; gs = []; ads = []; counts = []
    for number, ch in enumerate(m['chunks']):
        path = folder/ch['file']; assert file_sha(path) == ch['sha256']
        with np.load(path) as z:
            ii = z['spike_i']; t = z['spike_t']; tt = np.rint(t/.0001).astype(np.int64)
            assert np.allclose(t, tt*.0001, atol=1e-10, rtol=0)
            assert np.all((tt >= number*250) & (tt < (number+1)*250))
            np.testing.assert_array_equal(np.bincount(ii, minlength=138639)[targets], z['counts'][targets])
            indices.append(ii.copy()); ticks.append(tt)
            gs.append(z['g_mV'][columns]); counts.append(z['counts'][targets])
            ads.append(z['adapt_mV'][columns] if 'adapt_mV' in z else np.zeros(len(columns)))
    return m, np.concatenate(indices), np.concatenate(ticks), np.asarray(gs), np.asarray(ads), np.asarray(counts)


def main():
    start = time.monotonic()
    OUT.mkdir(exist_ok=False); space_check(OUT, 100*1024**2)
    p = json.loads((PRIOR/'protocol.json').read_text())
    pn = [p['mapping'][k][0]['index'] for k in ['DM1_lPN_left', 'DM1_lPN_right']]
    targets = pn+[x['index'] for x in p['selected_local_targets']]
    columns = [p['selected'].index(x) for x in targets]
    paths = [Path(__file__), ROOT/'flygarden/recorded_drive.py', ROOT/'flygarden/feedback_trace.py',
             ROOT/'tests/test_recorded_drive.py', PRIOR/'protocol.json', PRIOR/'calibration-results.json',
             BASE/'feedback-trace-v1/native-gate-validation.json', ROOT/'data/annotations.tsv',
             ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv', ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet']
    jobs = [f'{model}-{cue}-{seed}' for model in MODELS for seed in SEEDS for cue in CUES]
    paths += [PRIOR/'trials'/name/'manifest.json' for name in jobs]
    protocol = {'version': 1, 'scope': 'Descriptive delayed-input attribution, not a causal intervention or controller qualification.',
                'selection_basis': 'Original and the strongest preregistered setting in each of the two adaptation domains; both calibration seeds and all four existing cues.',
                'trials': jobs, 'targets': targets, 'clock_s': .0001, 'delay_ticks': 18,
                'phases_ticks': PHASES, 'state_replay_max_error_mV': 1e-10,
                'replay_scope': 'Observed spikes set resets/refractoriness. Independently reconstruct g and adapt at all 240 endpoints, not voltage or predicted spike times.',
                'drive_units': 'Voltage-equivalent signed synaptic increments in mV/s; not biological currents.',
                'pregate_arrivals_saved': True, 'native_full_brain_runs': 0,
                'controller_changes': 0, 'acceptance_criteria_changed': False,
                'source_hashes': {str(path.relative_to(ROOT)): file_sha(path) for path in paths}}
    atomic_json(OUT/'protocol.json', protocol)
    ids = pd.read_csv(ROOT/'vendor/fly-brain/data/2025_Completeness_783.csv', index_col=0).index.to_numpy(dtype=np.int64)
    ann = pd.read_csv(ROOT/'data/annotations.tsv', sep='\t', dtype={'root_id': str}, low_memory=False).fillna('').set_index('root_id').reindex([str(x) for x in ids]).fillna('')
    graph = pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                            columns=['Presynaptic_Index', 'Postsynaptic_Index', 'Excitatory x Connectivity'],
                            filters=[('Postsynaptic_Index', 'in', targets)])
    weights = csr_matrix((graph['Excitatory x Connectivity'].to_numpy()*.275,
                          ([targets.index(i) for i in graph.Postsynaptic_Index], graph.Presynaptic_Index)), shape=(len(targets), len(ids)))
    target_info = [{'index': t, 'root_id': str(ids[t]), 'cell_type': str(ann.iloc[t].cell_type),
                    'cell_class': str(ann.iloc[t].cell_class)} for t in targets]
    atomic_json(OUT/'targets.json', target_info)
    summaries = []; checks = []
    for number, name in enumerate(jobs):
        model = name.rsplit('-', 2)[0]
        m, ii, ticks, stored_g, stored_ad, counts = load_trial(PRIOR/'trials'/name, columns, targets)
        arrival_ticks = ticks+18
        impulses = delayed_impulses(ii, ticks, weights, 60000, 18)
        spikes = np.zeros((60000, len(targets)), bool)
        for j, target in enumerate(targets): spikes[ticks[ii == target], j] = True
        step = np.zeros(len(targets)); tau = .45
        if model != 'original':
            tau = p['parameters'][model]['tau_s']
            domain = set(p['domains'][model]['indices'])
            step = np.array([p['parameters'][model]['step_mv'] if t in domain else 0 for t in targets])
        g, ad, gates = replay_recorded_states(impulses, spikes, step, tau_s=tau)
        ge = float(np.max(np.abs(g-stored_g))); ae = float(np.max(np.abs(ad-stored_ad)))
        assert ge <= 1e-10 and ae <= 1e-10, (name, ge, ae)
        for j, target in enumerate(targets):
            np.testing.assert_array_equal(gates[:, j], refractory_gate(ticks[ii == target], 60000))
        checks.append({'trial': name, 'g_max_error_mV': ge, 'adapt_max_error_mV': ae,
                       'endpoints_checked': 240, 'target_count': len(targets), 'gate_exact': True})
        # Preserve pre-gate arrivals: altered dynamics would require new gates.
        space_check(OUT, impulses.nbytes+2*1024**2)
        path = OUT/(name+'-drive.npz')
        with path.with_suffix('.tmp').open('wb') as f:
            np.savez_compressed(f, target_indices=np.array(targets), arrivals_mV=impulses,
                                recorded_spikes=spikes, g_mV=g, adapt_mV=ad, counts_25ms=counts)
        path.with_suffix('.tmp').replace(path)
        for phase, (lo, hi) in PHASES.items():
            eligible = (arrival_ticks >= lo) & (arrival_ticks < hi)
            sources = ii[eligible]; arr = arrival_ticks[eligible]; duration = (hi-lo)*.0001
            contributions = []
            for j, target in enumerate(targets):
                pre_counts = np.bincount(sources, minlength=len(ids))
                accepted_counts = np.bincount(sources[gates[arr, j]], minlength=len(ids))
                row = weights.getrow(j); pre = row.indices
                values = accepted_counts[pre]*row.data/duration
                pregate = pre_counts[pre]*row.data/duration
                groups = {}; ranking = []
                for index, value, before in zip(pre, values, pregate):
                    if before == 0: continue
                    label = str(ann.iloc[index].cell_class) or 'unavailable'
                    group = groups.setdefault(label, {'positive_mV_per_s': 0., 'negative_mV_per_s': 0.,
                                                       'pregate_positive_mV_per_s': 0., 'pregate_negative_mV_per_s': 0.})
                    group['positive_mV_per_s' if value > 0 else 'negative_mV_per_s'] += abs(float(value))
                    group['pregate_positive_mV_per_s' if before > 0 else 'pregate_negative_mV_per_s'] += abs(float(before))
                    ranking.append({'index': int(index), 'root_id': str(ids[index]), 'cell_type': str(ann.iloc[index].cell_type),
                                    'cell_class': label, 'signed_accepted_mV_per_s': float(value), 'signed_pregate_mV_per_s': float(before)})
                # Independently cross-check accepted signed impulse accounting.
                assert abs(values.sum()-(impulses[lo:hi,j]*gates[lo:hi,j]).sum()/duration) < 1e-8
                contributions.append({**target_info[j], 'rate_hz': float(counts[lo//250:hi//250,j].sum()/duration),
                                      'positive_mV_per_s': float(values[values > 0].sum()), 'negative_mV_per_s': float(-values[values < 0].sum()),
                                      'pregate_positive_mV_per_s': float(pregate[pregate > 0].sum()), 'pregate_negative_mV_per_s': float(-pregate[pregate < 0].sum()),
                                      'by_class': groups, 'top_positive_sources': sorted([r for r in ranking if r['signed_accepted_mV_per_s'] > 0], key=lambda r: -r['signed_accepted_mV_per_s'])[:20],
                                      'top_negative_sources': sorted([r for r in ranking if r['signed_accepted_mV_per_s'] < 0], key=lambda r: r['signed_accepted_mV_per_s'])[:10]})
            summaries.append({'trial': name, 'phase': phase, 'inputs': contributions})
        atomic_json(OUT/'progress.json', {'status': 'running', 'completed': number+1, 'planned': len(jobs), 'trial': name})
        print(name, 'traced; g error', ge, 'adapt error', ae, flush=True)
    verified = all(file_sha(ROOT/key) == sha for key, sha in protocol['source_hashes'].items())
    assert verified
    result = {'status': 'complete', 'trials': len(jobs), 'chunks_audited': len(jobs)*240,
              'native_full_brain_runs': 0, 'controller_changed': False, 'sources_reverified': verified,
              'state_replay': checks, 'summaries': summaries, 'wall_seconds': time.monotonic()-start,
              'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT/'results.json', result)
    atomic_json(OUT/'progress.json', {'status': 'complete', 'completed': len(jobs), 'planned': len(jobs)})
    print('Completed in', round(result['wall_seconds'], 1), 'seconds', flush=True)


if __name__ == '__main__': main()

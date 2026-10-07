"""Isolated recorded-input diagnostic, never a replacement garden controller.

Replay recorded ORN spikes through the exact anatomical DM1 -> two-PN edges.
No recurrent edges, navigation decoder, support drive, or learning are present.
"""
import json, resource, sys, time
from pathlib import Path
import brian2 as b
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from flygarden.adaptive_neurons import adaptive_neurons
from flygarden.continuous_candidate import file_sha
from flygarden.feedback_trace import delayed_impulses
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
PRIOR = BASE/'adaptive-parameter-sweep-v1'
TRACE = BASE/'adaptive-feedback-trace-v1'
OUT = BASE/'dm1-feedforward-diagnostic-v1'
DT = .0001; STEPS = 60000


def native_replay(drive_mv, adapted, step_mv=13.5):
    """Recompute gates and threshold crossings from pre-gate arrival drive."""
    b.start_scope(); b.prefs.codegen.target = 'cython'
    clock = b.Clock(dt=DT*b.second)
    n = len(adapted)
    if np.any(adapted):
        cells = adaptive_neurons(n, clock, tau_s=.45, step_mv=step_mv, mask=np.asarray(adapted, bool))
    else:
        cells = b.NeuronGroup(n, '''dv/dt=(-52*mV-v+g)/(20*ms):volt (unless refractory)
            dg/dt=-g/(5*ms):volt (unless refractory)
            rfc:second''', threshold='v > -45*mV', reset='v=-52*mV;g=0*mV',
            refractory='rfc', method='linear', clock=clock)
        cells.v = -52*b.mV; cells.rfc = 2.2*b.ms
    drive = b.TimedArray(drive_mv*b.mV, dt=DT*b.second)
    # Explicit gating is required for run_regularly; Synapses normally supplies it.
    injection = cells.run_regularly('g += int(not_refractory)*drive(t,i)', when='synapses')
    spikes = b.SpikeMonitor(cells)
    keys = ['v', 'g']+(['adapt'] if np.any(adapted) else [])
    monitor = b.StateMonitor(cells, keys, record=True, when='end')
    net = b.Network(cells, injection, spikes, monitor)
    net.run(STEPS*DT*b.second, namespace={'drive': drive})
    ii = np.asarray(spikes.i[:], int); ticks = np.rint(spikes.t[:]/b.second/DT).astype(int)
    counts = np.zeros((240, n), np.int64); np.add.at(counts, (ticks//250, ii), 1)
    state = {key+'_mV': np.asarray(getattr(monitor, key)/b.mV)[:,249::250].T for key in keys}
    if 'adapt_mV' not in state: state['adapt_mV'] = np.zeros_like(state['g_mV'])
    return counts, ii, ticks, state


def main():
    start = time.monotonic(); OUT.mkdir(exist_ok=False); space_check(OUT, 100*1024**2)
    p = json.loads((PRIOR/'protocol.json').read_text())
    pn = [p['mapping'][k][0]['index'] for k in ['DM1_lPN_left', 'DM1_lPN_right']]
    orn = [x['index'] for k in ['ORN_DM1_left', 'ORN_DM1_right'] for x in p['mapping'][k]]
    parents = [f'original-{cue}-{seed}' for seed in [12001,12002] for cue in ['none','a_left','a_right','a_both']]
    validation = [f'{model}-a_left-{seed}' for model in ['original', 'projection_t450_b13p5', 'sensory_projection_t450_b13p5'] for seed in [12001,12002]]
    paths = [Path(__file__), ROOT/'flygarden/adaptive_neurons.py', ROOT/'flygarden/feedback_trace.py',
             PRIOR/'protocol.json', TRACE/'protocol.json', TRACE/'results.json',
             ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet']
    paths += [PRIOR/'trials'/name/'manifest.json' for name in parents]
    paths += [TRACE/(name+'-drive.npz') for name in validation]
    protocol = {'version': 1, 'registered_before_execution': True,
                'question': 'Does direct recorded DM1 ORN drive produce an opponent PN difference without recurrence, and does PN adaptation alter that conclusion?',
                'parents': parents, 'targets': pn, 'source_indices': orn,
                'scope': 'Reduced diagnostic with two electrical units; not a full-brain run or deployable controller. ORN spikes are from recorded full-network trials and can include their upstream feedback.',
                'removed': 'All drive except exact DM1 ORN-to-selected-PN edges; no recurrent connections, external PN stimulation, support, decoder, body, or learning.',
                'models': {'original': {'step_mV': 0}, 'pn_adaptive': {'tau_s': .45, 'step_mV': 13.5}},
                'clock_s': DT, 'delay_ticks': 18, 'pulse_windows': p['pulse_windows'], 'recovery_windows': p['recovery_windows'],
                'native_validation': {'parents': validation, 'predicted_target_spikes_exact': True, 'g_adapt_max_error_mV': 1e-10},
                'contrast_definition': 'Same as frozen Gate 3: left contrast minus right contrast >=10 Hz; left-minus-none>0; right-minus-none<0. Descriptive here, not qualification.',
                'acceptance_criteria_changed': False, 'promote_controller': False,
                'source_hashes': {str(path.relative_to(ROOT)): file_sha(path) for path in paths},
                'runtime': {'brian2': b.__version__, 'codegen': 'cython', 'numpy': np.__version__}}
    atomic_json(OUT/'protocol.json', protocol)
    validation_results = []
    for name in validation:
        with np.load(TRACE/(name+'-drive.npz')) as z:
            targets = z['target_indices']; adapted = np.zeros(len(targets), bool)
            if not name.startswith('original-'): adapted[:2] = True
            counts, ii, ticks, state = native_replay(z['arrivals_mV'], adapted)
            expected = z['recorded_spikes']; actual = np.zeros_like(expected)
            actual[ticks,ii] = True
            exact = np.array_equal(actual, expected) and np.array_equal(counts, z['counts_25ms'])
            errors = {k: float(np.max(abs(state[k]-z[k]))) for k in ['g_mV','adapt_mV']}
            assert exact and max(errors.values()) <= 1e-10, (name, exact, errors)
        validation_results.append({'parent': name, 'spikes_and_counts_exact': exact, 'errors_mV': errors, 'neurons': len(targets)})
        print('Native reconstruction passed:', name, flush=True)
    atomic_json(OUT/'native-reconstruction.json', validation_results)
    graph = pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                            columns=['Presynaptic_Index','Postsynaptic_Index','Excitatory x Connectivity','Connectivity'],
                            filters=[('Postsynaptic_Index','in',pn),('Presynaptic_Index','in',orn)])
    weights = csr_matrix((graph['Excitatory x Connectivity'].to_numpy()*.275,
                          ([pn.index(t) for t in graph.Postsynaptic_Index],graph.Presynaptic_Index)),shape=(2,138639))
    anatomy = []
    for key in ['ORN_DM1_left','ORN_DM1_right']:
        sources = [x['index'] for x in p['mapping'][key]]
        anatomy.append({'source': key, 'neuron_count': len(sources), 'signed_synaptic_sites': [float(weights[j,sources].sum()/.275) for j in range(2)]})
    atomic_json(OUT/'anatomy.json', anatomy)
    traces = {}; trial_results = []; drive_paths = []
    for name in parents:
        folder = PRIOR/'trials'/name; m = json.loads((folder/'manifest.json').read_text()); assert m['status'] == 'complete'
        indices = []; times = []
        for ch in m['chunks']:
            path = folder/ch['file']; assert file_sha(path) == ch['sha256']
            with np.load(path) as z:
                keep = np.isin(z['spike_i'], orn)
                indices.append(z['spike_i'][keep]); times.append(np.rint(z['spike_t'][keep]/DT).astype(int))
        drive = delayed_impulses(np.concatenate(indices), np.concatenate(times), weights, STEPS, 18)
        drive_path = OUT/(name+'-input.npz'); np.savez_compressed(drive_path, arrivals_mV=drive)
        drive_paths.append({'file': drive_path.name, 'sha256': file_sha(drive_path)})
        cue = m['case']; seed = m['seed']
        for model in ['original','pn_adaptive']:
            counts, ii, ticks, state = native_replay(drive, np.array([model != 'original']*2))
            traces[(model,seed,cue)] = counts/.025
            path = OUT/(model+'--'+name+'.npz')
            np.savez_compressed(path, counts_25ms=counts, spike_i=ii, spike_ticks=ticks, **state)
            trial_results.append({'model': model, 'seed': seed, 'cue': cue, 'parent': name, 'file': path.name, 'sha256': file_sha(path)})
            atomic_json(OUT/'progress.json', {'status': 'running', 'completed': len(trial_results), 'planned': 16})
        print('Feedforward replay complete:', name, flush=True)
    contrasts = []; recovery = []
    for model in ['original','pn_adaptive']:
        for seed in [12001,12002]:
            none = traces[(model,seed,'none')]
            for pulse,(lo,hi) in enumerate(p['pulse_windows'],1):
                values = {cue: float(np.diff(-traces[(model,seed,cue)][lo:hi], axis=1).mean()) for cue in ['none','a_left','a_right']}
                passed = values['a_left']-values['a_right']>=10 and values['a_left']-values['none']>0 and values['a_right']-values['none']<0
                contrasts.append({'model': model,'seed': seed,'pulse': pulse,'left': values['a_left'],'right': values['a_right'],'none': values['none'],'same_Gate3_definition_satisfied': bool(passed)})
            for cue in ['a_left','a_right','a_both']:
                rates = traces[(model,seed,cue)]
                for pulse,(lo,hi) in enumerate(p['recovery_windows'],1):
                    diff = rates[lo:hi].mean(axis=0)-none[lo:hi].mean(axis=0)
                    recovery.append({'model': model,'seed': seed,'cue': cue,'pulse': pulse,'pn_excess_hz': diff.tolist(),'within_5Hz': bool(np.max(abs(diff))<=5)})
    verified = all(file_sha(ROOT/key)==sha for key,sha in protocol['source_hashes'].items()); assert verified
    result = {'status': 'complete', 'full_brain_runs': 0,'isolated_native_validation_runs': len(validation_results),
              'isolated_feedforward_runs': len(trial_results),'controller_changed': False,'promoted': False,
              'sources_reverified': verified,'native_reconstruction': validation_results,'trials': trial_results,'input_files': drive_paths,
              'contrast': contrasts,'recovery': recovery,'wall_seconds': time.monotonic()-start,
              'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT/'results.json',result); atomic_json(OUT/'progress.json',{'status':'complete','completed':16,'planned':16})
    print('Diagnostic complete in',round(result['wall_seconds'],1),'seconds',flush=True)


if __name__ == '__main__': main()

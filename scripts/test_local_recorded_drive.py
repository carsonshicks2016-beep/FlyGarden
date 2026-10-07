"""Isolated strong-adaptation stress test with fixed recorded pre-gate drive.

This does not close the network loop, qualify biological parameters, or test
whether adapting local cells can extinguish full-network recurrence.
"""
import json, resource, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from scripts.diagnose_dm1_feedforward import native_replay
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json, space_check

BASE = ROOT/'reports/brain-integration/recovery'
TRACE = BASE/'adaptive-feedback-trace-v1'
OUT = BASE/'local-recorded-drive-reference-v1'


def main():
    start = time.monotonic(); OUT.mkdir(exist_ok=False); space_check(OUT, 30*1024**2)
    jobs = [f'original-{cue}-{seed}' for seed in [12001,12002] for cue in ['none','a_left','a_right','a_both']]
    paths = [Path(__file__), ROOT/'scripts/diagnose_dm1_feedforward.py', ROOT/'flygarden/adaptive_neurons.py',
             TRACE/'protocol.json', TRACE/'results.json', BASE/'local-source-qualification-v1/results.json']
    paths += [TRACE/(name+'-drive.npz') for name in jobs]
    protocol = {'version': 1, 'registered_before_execution': True, 'parents': jobs,
                'scope': 'Six isolated electrical units driven by saved original full-network incoming events. No reconnection to full graph; no effect on parent presynaptic trains.',
                'question': 'Can the already tested strong adaptation setting suppress the four selected local electrical units despite their continuing recorded input? Distinguish input-off recovery from continuing-input suppression.',
                'conditions': {'original': {'mask': [False]*6}, 'local_adaptive': {'mask': [False,False,True,True,True,True], 'tau_s': .45, 'step_mV': 13.5}},
                'parameter_basis': 'Strongest existing preregistered setting; fixed engineering stress reference, not a cell-type fit, newly optimized point or qualified full-network candidate.',
                'input': 'Same pre-gate 1.8ms-delayed signed arrivals in both conditions; native gates recomputed.',
                'pulse_off_reference': 'Two additional isolated runs use original-a_left-12001 drive only during [0.3,0.8018) and [3.3,3.8018), explicitly zeroing all other arrivals. This synthetic input-cut reference is not a full-network lesion.',
                'acceptance': {'original_spikes_counts_exact': True, 'original_g_adapt_error_mV': 1e-10, 'unchanged_PN_spikes_exact': True, 'finite_states': True},
                'recovery_windows': [[100,120],[220,240]], 'pulse_windows': [[12,32],[132,152]],
                'interpretation': 'Recovery excess >5Hz does not qualify quiet recovery under fixed continuing drive. Full-network extinction, revised Gate3, behavior and learning are not evaluated.',
                'full_brain_runs': 0, 'promote': False, 'source_hashes': {str(p.relative_to(ROOT)): file_sha(p) for p in paths}}
    atomic_json(OUT/'protocol.json', protocol)
    traces = {}; trials = []
    for name in jobs:
        with np.load(TRACE/(name+'-drive.npz')) as z:
            original_spikes = z['recorded_spikes']; reference = {}
            for condition, mask in [('original',[False]*6), ('local_adaptive',[False,False,True,True,True,True])]:
                counts, ii, ticks, state = native_replay(z['arrivals_mV'], np.array(mask, bool))
                actual = np.zeros_like(original_spikes); actual[ticks,ii] = True
                assert all(np.isfinite(v).all() for v in state.values())
                errors = {}
                if condition == 'original':
                    assert np.array_equal(actual,original_spikes) and np.array_equal(counts,z['counts_25ms'])
                    errors = {k:float(np.max(abs(state[k]-z[k]))) for k in ['g_mV','adapt_mV']}; assert max(errors.values())<=1e-10
                else: assert np.array_equal(actual[:,:2],original_spikes[:,:2]), 'Fixed-input PN control changed'
                path = OUT/(condition+'--'+name+'.npz')
                np.savez_compressed(path, counts_25ms=counts, spike_i=ii, spike_ticks=ticks, **state)
                _,cue,seed = name.rsplit('-',2); traces[(condition,int(seed),cue)] = counts/.025
                trials.append({'parent':name,'condition':condition,'file':path.name,'sha256':file_sha(path),'reference_errors_mV':errors})
                reference[condition] = counts
        print(name, 'original reconstruction and local stress test complete', flush=True)
        atomic_json(OUT/'progress.json',{'status':'running','completed':len(trials),'planned':18})
    pulse_off = []
    with np.load(TRACE/'original-a_left-12001-drive.npz') as z:
        drive = np.zeros_like(z['arrivals_mV'])
        for lo,hi in [(3000,8018),(33000,38018)]: drive[lo:hi] = z['arrivals_mV'][lo:hi]
        for condition,mask in [('original',[False]*6),('local_adaptive',[False,False,True,True,True,True])]:
            counts,ii,ticks,state = native_replay(drive,np.array(mask,bool))
            assert all(np.isfinite(v).all() for v in state.values())
            rates = [counts[lo:hi,2:].sum(axis=0)/((hi-lo)*.025) for lo,hi in protocol['recovery_windows']]
            assert all(np.max(rate)<=5 for rate in rates), ('Pulse-off reference did not settle',condition,rates)
            path = OUT/(condition+'--synthetic-pulse-off.npz')
            np.savez_compressed(path,counts_25ms=counts,spike_i=ii,spike_ticks=ticks,**state)
            pulse_off.append({'condition':condition,'file':path.name,'sha256':file_sha(path),'local_recovery_rates_hz':[r.tolist() for r in rates]})
    comparisons = []
    for seed in [12001,12002]:
        for cue in ['a_left','a_right','a_both']:
            for pulse,(lo,hi) in enumerate(protocol['recovery_windows'],1):
                data = {}
                for condition in ['original','local_adaptive']:
                    rates = traces[(condition,seed,cue)][lo:hi,2:].mean(axis=0)
                    none = traces[(condition,seed,'none')][lo:hi,2:].mean(axis=0)
                    data[condition] = {'individual_local_rates_hz':rates.tolist(), 'local_excess_hz':(rates-none).tolist(),
                                       'within_existing_5Hz_recovery_bound': bool(np.max(abs(rates-none))<=5)}
                comparisons.append({'seed':seed,'cue':cue,'pulse':pulse,**data})
    assert all(file_sha(ROOT/k)==v for k,v in protocol['source_hashes'].items())
    result = {'status':'complete','full_brain_runs':0,'isolated_runs':18,'native_original_reconstruction_exact':True,
              'PN_control_unchanged':True,'production_changes':0,'trials':trials,'recovery_comparisons':comparisons,
              'synthetic_pulse_off_reference':pulse_off,
              'scope':protocol['scope'],'wall_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    atomic_json(OUT/'results.json',result);atomic_json(OUT/'progress.json',{'status':'complete','completed':18,'planned':18})
    print('Completed in',round(result['wall_seconds'],2),'seconds',flush=True)


if __name__=='__main__': main()

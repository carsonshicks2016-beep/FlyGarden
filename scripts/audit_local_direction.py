"""Offline raw-spike, motor, legacy-gate and continuation audit; no simulations."""
import hashlib
import json
import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT));sys.path.insert(0, str(ROOT / 'scripts'))
import sweep_adaptive_lif as reference
from flygarden.continuous_candidate import file_sha
from flygarden.directional_metrics import evaluate_traces
from flygarden.recording import atomic_json

OUT = ROOT / 'reports/brain-integration/recovery/local-adaptation-direction-v1'
KEYS = ['DM1_lPN_left', 'DM1_lPN_right', 'DNa02_left', 'DNa02_right', 'DNp09_left', 'DNp09_right']


def main():
    p = json.loads((OUT / 'protocol.json').read_text())
    results = json.loads((OUT / 'results.json').read_text())
    assert results['protocol_sha256'] == file_sha(OUT / 'protocol.json')
    assert all(file_sha(ROOT / name) == digest for name, digest in p['sources'].items())
    parent = json.loads((ROOT / 'reports/brain-integration/recovery/local-adaptation-closed-loop-v1/protocol.json').read_text())
    assert p['domains'] == parent['domains'] and p['parameters'] == parent['parameters']
    assert all(p['gates'][key] == value for key, value in parent['gates'].items())
    groups = [[x['index'] for x in p['mapping'][key]] for key in KEYS]
    groups += [[x['index']] for x in p['selected_local_targets']]
    traces, external, weight_hashes = {}, {}, set()
    chunks = 0;continuations = [];activity = []
    excluded = np.ones(138639, dtype=bool);excluded[p['domains']['local_adaptive']['indices']] = False
    for model in p['models']:
        for seed in p['validation_seeds']:
            for cue in p['cues']:
                folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
                m = json.loads((folder / 'manifest.json').read_text())
                rows = json.loads((folder / 'rows.json').read_text())
                assert m['status'] == 'complete' and len(m['chunks']) == len(rows) == 240
                assert m['sources'] == p['sources'] and m['protocol_sha256'] == results['protocol_sha256']
                assert m['controller']['neurons'] == 138639 and m['controller']['connections'] == 15091983
                assert m['initial_weight_hash'] == m['final_weight_hash'] and m['learning_updates'] == 0
                weight_hashes.add(m['initial_weight_hash'])
                rates = [];total = [];motor = np.zeros(2)
                for tick, (chunk, row) in enumerate(zip(m['chunks'], rows)):
                    file = folder / chunk['file'];assert file_sha(file) == chunk['sha256']
                    with np.load(file) as data:
                        ids = data['spike_i']
                        assert np.array_equal(np.bincount(ids, minlength=138639), data['counts'])
                        rate = np.array([np.count_nonzero(np.isin(ids, group)) / len(group) / .025 for group in groups])
                        rates.append(rate);total.append(len(ids))
                        assert np.array_equal(rate[:6], [row['population_hz'][key] for key in KEYS])
                        assert abs(row['end'] - (tick + 1) * .025) < 1e-9
                        assert not len(ids) or (data['spike_t'].min() >= tick * .025 - 1e-9 and data['spike_t'].max() < (tick + 1) * .025 + 1e-9)
                        assert np.max(abs(data['spike_t'] / .0001 - np.rint(data['spike_t'] / .0001)), initial=0) < 1e-7
                        concentrations = p['sensory_cases'][cue] if (12 <= tick < 32 or 132 <= tick < 152) else [0, 0]
                        requested = {'ORN_DM1_left': 50 * concentrations[0], 'ORN_DM1_right': 50 * concentrations[1],
                                     'ORN_DM2_left': 0, 'ORN_DM2_right': 0, 'DNp09_left': 65, 'DNp09_right': 65,
                                     'LPLC2_left': 0, 'LPLC2_right': 0}
                        assert row['requested_hz'] == requested
                        digest = hashlib.sha256(data['external_i'].tobytes() + data['external_t'].tobytes()).hexdigest()
                        key = (seed, cue, tick)
                        if key in external:assert digest == external[key]
                        else:external[key] = digest
                        forward = np.clip(rate[4:6].mean() / 100, 0, 1)
                        turn = np.clip((rate[2] - rate[3]) / 100, -1, 1)
                        desired = np.clip([forward - .5 * turn, forward + .5 * turn], 0, 1.2)
                        alpha = 1 - np.exp(-.025 / .4481420117724551)
                        motor = (1 - alpha) * motor + alpha * desired
                        assert np.array_equal(motor, data['motor']) and np.array_equal(motor, row['motor'])
                    chunks += 1
                traces[(model, seed, cue)] = np.array(rates)
                activity.append({'trial': folder.name, 'whole_network_spikes': int(sum(total)),
                                 'pulse_spikes': [int(sum(total[lo:hi])) for lo, hi in p['pulse_windows']],
                                 'last_half_second_spikes': int(sum(total[220:240]))})
                if cue == 'a_left':
                    receipt = json.loads((folder / 'continuation-result.json').read_text())
                    assert receipt['status'] == 'passed' and receipt['fresh_process'] and receipt['windows'] == 5
                    assert max(receipt['errors_mV'].values()) <= p['gates']['state_precision_mV']
                    integrity = json.loads((folder / 'checkpoint/integrity.json').read_text())
                    assert all(file_sha(folder / 'checkpoint' / name) == sha for name, sha in integrity['files'].items())
                    with np.load(folder / 'continuation-state.npz') as state:
                        if model == 'local_adaptive':assert np.count_nonzero(state['adapt'][excluded]) == 0
                        else:assert 'adapt' not in state.files
                    continuations.append({'trial': folder.name, **receipt})
    assert weight_hashes == {'f6f6ab9f7c49e14a906d120c705e6af7814ecdeeecaaefad8b1280bdb71e7732'}
    rebuilt = evaluate_traces(p, traces)
    assert all(rebuilt[key] == results[key] for key in rebuilt)
    # Separate globals redirect only this copied function. Frozen module/code/files are unmodified.
    legacy_evaluate = types.FunctionType(reference.evaluate.__code__, {**reference.evaluate.__globals__, 'OUT': OUT})
    legacy = legacy_evaluate(p, p['models'], p['validation_seeds'], p['cues'])
    for group in ['recovery', 'contrast', 'bursts', 'support', 'gradient']:
        assert len(legacy[group]) == len(results[group])
        assert all(all(new[key] == value for key, value in old.items()) for old, new in zip(legacy[group], results[group])), group
    assert legacy['eligible'] == results['primary_neural_gates_passed']
    interrupted = json.loads((OUT / 'interruption-test.json').read_text())
    finished = json.loads((OUT / 'trials' / interrupted['trial'] / 'manifest.json').read_text())
    prefix = interrupted['complete_prefix']
    assert interrupted['controlled_termination'] and finished['reconstructed_windows'] == len(prefix)
    assert finished['chunks'][:len(prefix)] == prefix and len(finished['chunks']) == 240
    interrupted.update(status='passed', reconstructed_windows=len(prefix), complete_prefix_unchanged=True)
    atomic_json(OUT / 'interruption-test.json', interrupted)
    audit = {'status': 'passed', 'chunks_audited': chunks, 'trial_count': 28,
             'raw_spike_metrics_exact': True, 'original_evaluator_all_primary_gates_exact': True,
             'frozen_module_unmodified': True, 'paired_external_inputs_exact': True,
             'motor_commands_reconstructed_exact': True, 'clock_and_requested_rates_verified': True,
             'weights_sha256': next(iter(weight_hashes)), 'adaptation_outside_mask_zero': True,
             'continuations': continuations, 'whole_network_activity': activity,
             'sources_reverified': True, 'source_sha256': file_sha(Path(__file__)),
             'interruption_and_reconstruction': {'status': 'passed', 'trial': interrupted['trial'],
                                                 'reconstructed_windows': len(prefix), 'complete_prefix_unchanged': True},
             'controller_promoted': False, 'scope': 'Bounded engineering neural screen; no behavioral/learning or biological validation.'}
    atomic_json(OUT / 'independent-audit.json', audit)
    print('Passed raw-spike/motor/clock checks and exact original-gate parity:', chunks, 'chunks.', flush=True)


if __name__ == '__main__':main()

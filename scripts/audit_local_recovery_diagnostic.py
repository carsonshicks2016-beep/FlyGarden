"""Independent offline gate reconstruction from individual recorded spikes.

Does not import the neural evaluator or construct a simulated network. Raw
recordings and checkpoints are intentionally local, outside the Git snapshot.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/brain-integration/recovery/local-adaptation-closed-loop-v1'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    protocol = json.loads((OUT / 'protocol.json').read_text())
    results = json.loads((OUT / 'results.json').read_text())
    assert all(sha(ROOT / name) == expected for name, expected in protocol['sources'].items())
    keys = ['DM1_lPN_left', 'DM1_lPN_right', 'DNa02_left', 'DNa02_right', 'DNp09_left', 'DNp09_right']
    groups = [[x['index'] for x in protocol['mapping'][key]] for key in keys]
    groups += [[x['index']] for x in protocol['selected_local_targets']]
    traces, delivered, totals, weights = {}, {}, {}, set()
    chunks, continuation_count = 0, 0
    excluded = np.ones(138639, dtype=bool)
    excluded[protocol['domains']['local_adaptive']['indices']] = False
    for model in protocol['models']:
        for seed in protocol['calibration_seeds']:
            for cue in protocol['cues']:
                folder = OUT / 'trials' / f'{model}-{cue}-{seed}'
                manifest = json.loads((folder / 'manifest.json').read_text())
                assert manifest['status'] == 'complete' and len(manifest['chunks']) == 240
                assert manifest['initial_weight_hash'] == manifest['final_weight_hash']
                weights.add(manifest['initial_weight_hash'])
                rates, whole = [], []
                for chunk in manifest['chunks']:
                    file = folder / chunk['file']
                    assert sha(file) == chunk['sha256']
                    with np.load(file) as data:
                        indices = data['spike_i']
                        assert np.array_equal(np.bincount(indices, minlength=138639), data['counts'])
                        # Compute selected rates from spike identities, not population summaries.
                        rates.append([np.count_nonzero(np.isin(indices, group)) / len(group) / .025
                                      for group in groups])
                        whole.append(len(indices))
                        digest = hashlib.sha256(data['external_i'].tobytes() + data['external_t'].tobytes()).hexdigest()
                        key = (seed, cue, chunk['file'])
                        if key in delivered:
                            assert digest == delivered[key]
                        else:
                            delivered[key] = digest
                    chunks += 1
                traces[(model, seed, cue)] = np.array(rates)
                totals[(model, seed, cue)] = np.array(whole)
                if cue == 'a_left':
                    continuation = json.loads((folder / 'continuation-result.json').read_text())
                    assert continuation['status'] == 'passed' and continuation['fresh_process']
                    assert continuation['windows'] == 5 and max(continuation['errors_mV'].values()) == 0
                    with np.load(folder / 'continuation-state.npz') as state:
                        if model == 'local_adaptive':
                            assert np.count_nonzero(state['adapt'][excluded]) == 0
                        else:
                            assert 'adapt' not in state.files
                    continuation_count += 1
    assert weights == {'f6f6ab9f7c49e14a906d120c705e6af7814ecdeeecaaefad8b1280bdb71e7732'}
    g = protocol['gates']
    checks = []
    for record in results['records']:
        model, seed, pulse = record['model'], record['seed'], record['pulse']
        odor, none = traces[(model, seed, 'a_left')], traces[(model, seed, 'none')]
        lo, hi = protocol['pulse_windows'][pulse - 1]
        rlo, rhi = protocol['recovery_windows'][pulse - 1]
        pn, neutral = odor[:, :2].mean(1), none[:, :2].mean(1)
        gain = float(pn[lo:hi].mean() - (neutral[lo:hi].mean() if pulse == 1 else pn[100:120].mean()))
        pn_difference = odor[rlo:rhi, :2].mean(0) - none[rlo:rhi, :2].mean(0)
        local_difference = odor[rlo:rhi, 6:].mean(0) - none[rlo:rhi, 6:].mean(0)
        dna = float((odor[:, 2] - odor[:, 3] - none[:, 2] + none[:, 3])[rlo:rhi].mean())
        assert gain == record['gain_hz']
        assert np.array_equal(pn_difference, record['pn_recovery_difference_hz'])
        assert np.array_equal(local_difference, record['local_recovery_difference_hz'])
        assert dna == record['signed_dna_recovery_difference_hz']
        assert (gain >= g['response_gain_hz']) == record['response_passed']
        assert (max(abs(pn_difference)) <= g['individual_PN_and_local_recovery_difference_hz']) == record['PN_recovery_passed']
        assert (max(abs(local_difference)) <= g['individual_PN_and_local_recovery_difference_hz']) == record['local_recovery_passed']
        assert (abs(dna) <= g['signed_DNa02_recovery_difference_hz']) == record['DNa02_recovery_passed']
        checks.append({'model': model, 'seed': seed, 'pulse': pulse, 'raw_spike_metric_match_exact': True})
    for burst in results['bursts']:
        model, seed = burst['model'], burst['seed']
        odor, none = traces[(model, seed, 'a_left')], traces[(model, seed, 'none')]
        excess = (odor[:, :2] - none[:, :2]).mean(1)
        lo, hi = burst['window']
        maximum = max(float(excess[i:i+4].mean()) for i in range(lo, hi - 3))
        assert maximum == burst['max_100ms_PN_excess_hz']
        assert (maximum <= g['burst_100ms_recovery_PN_difference_hz']) == burst['passed']
    for support in results['support']:
        model, seed = support['model'], support['seed']
        rates = traces[(model, seed, 'none')][:, 4:6].mean(0)
        original = traces[('original', seed, 'none')][:, 4:6].mean(0)
        assert bool(np.all(rates >= g['walking_support_retention_fraction'] * original)) == support['passed']
    activity = []
    for seed in protocol['calibration_seeds']:
        for cue in protocol['cues']:
            total = totals[('local_adaptive', seed, cue)]
            rates = traces[('local_adaptive', seed, cue)]
            activity.append({'trial': f'local_adaptive-{cue}-{seed}',
                             'support_mean_hz': rates[:, 4:6].mean(0).tolist(),
                             'final_half_second_total_spikes': int(total[220:240].sum()),
                             'odor_pulse_total_spikes': [int(total[lo:hi].sum()) for lo, hi in protocol['pulse_windows']]})
    audit = {'status': 'passed',
             'scope': 'Independent metric reconstruction from raw spikes; paired delivery/weights, fresh continuation receipts and nonselected adaptation state checked. Only the preregistered one-sided screen is qualified.',
             'chunks_audited': chunks, 'metric_checks': checks,
             'learning_weights_hash': next(iter(weights)),
             'adaptation_outside_395_local_mask_zero': True,
             'continuation_receipts_passed': continuation_count,
             'not_whole_brain_silencing': activity, 'sources_reverified': True,
             'audit_source_sha256': sha(Path(__file__))}
    (OUT / 'independent-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(f'Passed: {chunks} chunks, {len(checks)} metric records, {continuation_count} continuation receipts.')


if __name__ == '__main__':
    main()

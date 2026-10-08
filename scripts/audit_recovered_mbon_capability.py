"""Independent raw-spike, input RNG, clock, motor and capability-bound audit."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json

OUT = ROOT/'reports/brain-integration/recovery/recovered-mbon32-capability-v1'


def main():
    p = json.loads((OUT/'protocol.json').read_text()); r = json.loads((OUT/'results.json').read_text())
    assert r['status'] == 'complete' and r['protocol_sha256'] == file_sha(OUT/'protocol.json')
    assert all(file_sha(ROOT/key) == value for key, value in p['sources'].items())
    keys = ['MBON32_left', 'MBON32_right', 'DNa02_left', 'DNa02_right', 'DNp09_left', 'DNp09_right', 'DM1_lPN_left', 'DM1_lPN_right']
    targets = [p['mapping'][key][0]['index'] for key in keys]+[x['index'] for x in p['selected_local_targets']]
    traces = {}; chunks = 0; support_train = {}; direct_train = {}; maximum_motor_error = 0.
    for seed in p['diagnostic_seeds']:
        for case in p['cases']:
            folder = OUT/'trials'/f'{case}-{seed}'; m = json.loads((folder/'manifest.json').read_text())
            rows = json.loads((folder/'rows.json').read_text())
            assert m['status'] == 'complete' and len(m['chunks']) == len(rows) == 240
            assert m['initial_weight_hash'] == m['final_weight_hash'] and m['learning_updates'] == 0
            assert m['sources'] == p['sources'] and m['protocol_sha256'] == file_sha(OUT/'protocol.json')
            direct_meta = m['controller']['direct_capability_input']
            assert direct_meta['additional_zero_refractory_indices'] == p['direct_targets']
            channels = np.asarray(m['controller']['input_channels'])
            rng = np.random.default_rng(seed); direct_rng = np.random.default_rng(seed+100000)
            rates = np.zeros(8); rates[4:6] = 65
            recorded = []; motor = np.zeros(2)
            for tick, chunk in enumerate(m['chunks']):
                path = folder/chunk['file']; assert file_sha(path) == chunk['sha256']
                offsets, si = np.nonzero(rng.random((250, len(channels))) < rates[channels]*.0001)
                direct_rates = np.zeros(2)
                if any(lo <= tick < hi for lo, hi in p['pulse_windows']):
                    if case in ['left', 'both']: direct_rates[0] = 50
                    if case in ['right', 'both']: direct_rates[1] = 50
                mo, mi = np.nonzero(direct_rng.random((250, 2)) < direct_rates*.0001)
                with np.load(path) as z:
                    counts = np.bincount(z['spike_i'], minlength=138639)
                    np.testing.assert_array_equal(counts, z['counts'])
                    st = np.rint(z['spike_t']/.0001).astype(np.int64)
                    assert np.allclose(z['spike_t'], st*.0001, atol=1e-10, rtol=0)
                    assert ((st >= tick*250) & (st < (tick+1)*250)).all()
                    np.testing.assert_array_equal(z['external_i'], si)
                    np.testing.assert_array_equal(np.rint(z['external_t']/.0001).astype(np.int64), tick*250+offsets)
                    np.testing.assert_array_equal(z['mbon_i'], mi)
                    np.testing.assert_array_equal(np.rint(z['mbon_t']/.0001).astype(np.int64), tick*250+mo)
                    np.testing.assert_array_equal(z['mbon_delivered_i'], mi)
                    np.testing.assert_allclose(z['mbon_delivered_t'], z['mbon_t'], atol=1e-12, rtol=0)
                    digest = hashlib.sha256(z['external_i'].tobytes()+z['external_t'].tobytes()).hexdigest()
                    if (seed, tick) in support_train: assert digest == support_train[seed, tick]
                    else: support_train[seed, tick] = digest
                    for side in [0, 1]:
                        if case in (['left', 'both'] if side == 0 else ['right', 'both']):
                            times = z['mbon_t'][z['mbon_i'] == side]
                            digest = hashlib.sha256(times.tobytes()).hexdigest()
                            if (seed, tick, side) in direct_train: assert digest == direct_train[seed, tick, side]
                            else: direct_train[seed, tick, side] = digest
                    expected = {key: float(counts[[n['index'] for n in pop]].mean()/.025) if pop else None for key, pop in p['mapping'].items()}
                    assert expected == rows[tick]['population_hz']
                    assert rows[tick]['requested_hz'] == {key: float(rates[k]) for k, key in enumerate(['ORN_DM1_left', 'ORN_DM1_right', 'ORN_DM2_left', 'ORN_DM2_right', 'DNp09_left', 'DNp09_right', 'LPLC2_left', 'LPLC2_right'])}
                    forward = np.clip((expected['DNp09_left']+expected['DNp09_right'])/2/100, 0, 1)
                    turn = np.clip((expected['DNa02_left']-expected['DNa02_right'])/100, -1, 1)
                    desired = np.clip([forward-.5*turn, forward+.5*turn], 0, 1.2)
                    alpha = 1-np.exp(-.025/.4481420117724551); motor = (1-alpha)*motor+alpha*desired
                    maximum_motor_error = max(maximum_motor_error, float(max(abs(motor-z['motor']))))
                    np.testing.assert_array_equal(motor, z['motor']); np.testing.assert_array_equal(motor, rows[tick]['motor'])
                    assert all(np.isfinite(z[k]).all() for k in z.files)
                    assert z['v_mV'].shape == z['g_mV'].shape == z['adapt_mV'].shape == (len(p['selected']),)
                    assert not z['adapt_mV'][[p['selected'].index(i) for i in p['direct_targets']]].any()
                    recorded.append(counts[targets]/.025)
                assert abs(chunk['end']-(tick+1)*.025) <= 1e-10 and rows[tick]['end'] == chunk['end']
                chunks += 1
            traces[seed, case] = np.asarray(recorded)

    def trace(seed, case, lo, hi): return traces[seed, case][lo:hi].sum(0)/(hi-lo)
    for row in r['direction']:
        seed = row['seed']; lo, hi = p['pulse_windows'][row['pulse']-1]
        values = {c: float(trace(seed, c, lo, hi)[2]-trace(seed, c, lo, hi)[3]) for c in p['cases']}
        differences = {c: values[c]-values['none'] for c in ['left', 'right', 'both']}
        flags = [differences['left'] >= 5, differences['right'] <= -5, abs(differences['both']) <= 5,
                 values['left']-values['right'] >= 10 and values['left'] > values['none'] and values['right'] < values['none']]
        assert values == row['contrast_hz'] and differences == row['delta_from_none_hz']
        assert row['passed'] == all(flags) and row['separation_hz'] == values['left']-values['right']
        for field, value in zip(['left_delta_at_least_5Hz', 'right_delta_at_most_minus_5Hz', 'bilateral_delta_within_5Hz', 'existing_descending_opponent_bound'], flags): assert row[field] == value
    for row in r['responses']:
        lo, hi = p['pulse_windows'][row['pulse']-1]; seed = row['seed']; case = row['case']; sides = row['stimulated_sides']
        t = trace(seed, case, lo, hi); n = trace(seed, 'none', lo, hi)
        previous = n if row['pulse'] == 1 else trace(seed, case, 100, 120)
        gains = t[sides]-n[sides]; renewed = t[sides]-previous[sides]
        assert row['matched_control_gain_hz'] == gains.tolist() and row['gain_from_previous_recovery_hz'] == renewed.tolist()
        assert row['passed'] == bool(np.all(gains >= 10) and np.all(renewed >= 10))
    for row in r['recovery']:
        lo, hi = p['recovery_windows'][row['pulse']-1]
        delta = trace(row['seed'], row['case'], lo, hi)-trace(row['seed'], 'none', lo, hi)
        assert row['individual_difference_hz'] == delta.tolist()
        assert row['passed'] == bool(max(abs(delta[:2])) <= 5 and max(abs(delta[6:])) <= 5 and abs(delta[2]-delta[3]) <= 5)
    for row in r['support_perturbation']:
        lo, hi = p['pulse_windows' if row['phase'] == 'pulse' else 'recovery_windows'][row['pulse']-1]
        actual = trace(row['seed'], row['case'], lo, hi)[4:6]; none = trace(row['seed'], 'none', lo, hi)[4:6]
        assert row['actual_hz'] == actual.tolist() and row['matched_candidate_none_hz'] == none.tolist()
        assert row['passed'] == bool(np.all(none > 0) and np.all(actual >= .8*none))
    for row in r['bursts']:
        lo, hi = row['window']; excess = traces[row['seed'], row['case']]-traces[row['seed'], 'none']
        totals = np.cumsum(np.vstack([np.zeros((1, 12)), excess]), axis=0)
        moving = (totals[lo+4:hi+1]-totals[lo:hi-3])/4
        mbon = moving[:, :2].max(0).tolist(); pn = float(moving[:, 6:8].mean(1).max())
        assert row['MBON_100ms_excess_hz'] == mbon and row['PN_100ms_excess_hz'] == pn
        assert row['passed'] == (max(mbon) <= 20 and pn <= 20)
    families = ['direction', 'responses', 'recovery', 'support_perturbation', 'bursts']
    assert r['capability_neural_checks_passed'] == all(x['passed'] for key in families for x in r[key])
    for seed in p['diagnostic_seeds']:
        folder = OUT/'trials'/f'left-{seed}'; receipt = json.loads((folder/'continuation-result.json').read_text())
        assert receipt['status'] == 'passed' and receipt['fresh_process'] and max(receipt['errors_mV'].values()) <= 1e-10
        integrity = folder/'checkpoint/integrity.json'; assert receipt['checkpoint_integrity_sha256'] == file_sha(integrity)
        for path, digest in json.loads(integrity.read_text())['files'].items(): assert file_sha(integrity.parent/path) == digest
    interrupted = json.loads((OUT/'interruption-test.json').read_text())
    m = json.loads((OUT/'trials'/interrupted['trial']/'manifest.json').read_text())
    assert interrupted['status'] == 'passed' and interrupted['prefix_reconstructed_exactly']
    assert m['chunks'][:len(interrupted['complete_prefix'])] == interrupted['complete_prefix']
    assert all(file_sha(ROOT/key) == value for key, value in p['sources'].items())
    atomic_json(OUT/'independent-audit.json', dict(status='passed', protocol_sha256=file_sha(OUT/'protocol.json'),
        source_sha256=file_sha(Path(__file__)), chunks_rehashed=chunks, raw_counts_exact=True,
        spike_clock_and_half_open_chunks_valid=True, support_inputs_identical_across_cases=True,
        left_right_direct_trains_match_bilateral=True, requested_and_generator_delivered_events_exact=True,
        motor_decoder_exact=True, maximum_motor_error=maximum_motor_error,
        capability_metrics_checked=sum(len(r[k]) for k in families), two_checkpoint_receipts_and_file_hashes_valid=True,
        interrupted_prefix_preserved=True, sources_reverified=True, controller_promoted=False))
    print('Independent audit passed;', chunks, 'chunks; all input, clock, motor and metric checks.', flush=True)


if __name__ == '__main__': main()

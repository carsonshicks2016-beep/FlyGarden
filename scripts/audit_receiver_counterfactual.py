"""Direct-event and closed-form audit without Brian2 or the replay helper."""
import gc
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flygarden.recording import atomic_json

OUT = ROOT/'reports/brain-integration/recovery/receiver-counterfactual-v1'
PRIOR = ROOT/'reports/brain-integration/recovery/local-adaptation-direction-v1'
CONDITIONS = ['intact', 'pn_dm1_only', 'dna_without_aotu019']


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024**2), b''): digest.update(block)
    return digest.hexdigest()


def main():
    started = time.monotonic()
    p = json.loads((OUT/'protocol.json').read_text())
    r = json.loads((OUT/'results.json').read_text())
    assert r['status'] == 'complete' and sha(OUT/'protocol.json') == r['protocol_sha256']
    assert all(sha(ROOT/key) == value for key, value in p['source_hashes'].items())
    assert len(r['trials']) == 84 and len(r['input_files']) == 28
    targets = [x['index'] for x in p['targets']]
    graph = pd.read_parquet(ROOT/'vendor/fly-brain/data/2025_Connectivity_783.parquet',
                           filters=[('Postsynaptic_Index', 'in', targets)])
    dense = []
    for node in p['targets']:
        rows = graph[graph.Postsynaptic_Index.eq(node['index'])]
        assert (rows.Postsynaptic_ID.astype(str) == node['root_id']).all()
        dense.append(np.bincount(rows.Presynaptic_Index,
                                 weights=rows['Excitatory x Connectivity']*.275, minlength=138639))
    masks = [np.ones(138639, bool) for _ in range(2)]
    masks[0][:] = False; masks[0][p['receptor_indices']] = True
    masks[1][[x['index'] for x in p['aotu_sources']]] = False
    removed = graph[graph.Presynaptic_Index.isin([x['index'] for x in p['aotu_sources']]) &
                    graph.Postsynaptic_Index.isin(targets[2:])]
    assert len(removed) == 3 and int(removed.Connectivity.sum()) == 338
    assert sorted(removed.to_dict('records'), key=lambda x: (x['Presynaptic_Index'], x['Postsynaptic_Index'])) == \
        sorted(p['removed_edges'], key=lambda x: (x['Presynaptic_Index'], x['Postsynaptic_Index']))

    # One simultaneous vector of 84 x four units, independent of native replay.
    drive = np.empty((60000, 336), float)
    expected_spikes = np.zeros((60000, 336), bool)
    expected_counts = np.empty((240, 336), np.int64)
    expected_state = {key: np.empty((240, 336), float) for key in ['v_mV', 'g_mV']}
    records = {(x['parent'], x['condition']): x for x in r['trials']}
    inputs = {x['parent']: x for x in r['input_files']}
    traces = {}; chunks = 0; maximum_drive_error = 0.
    for number, name in enumerate(p['trials']):
        m = json.loads((PRIOR/'trials'/name/'manifest.json').read_text())
        ii = []; tt = []
        for k, ch in enumerate(m['chunks']):
            path = PRIOR/'trials'/name/ch['file']; assert sha(path) == ch['sha256']
            with np.load(path) as z:
                indices = z['spike_i']; ticks = np.rint(z['spike_t']/.0001).astype(np.int64)
                assert np.all((ticks >= k*250) & (ticks < (k+1)*250))
                np.testing.assert_array_equal(np.bincount(indices, minlength=138639), z['counts'])
                ii.append(indices.copy()); tt.append(ticks)
            chunks += 1
        ii = np.concatenate(ii); tt = np.concatenate(tt)
        arrivals = tt+18; valid = arrivals < 60000
        events = ii[valid]; arrivals = arrivals[valid]
        input_path = OUT/inputs[name]['file']; assert sha(input_path) == inputs[name]['sha256']
        with np.load(input_path) as z:
            for arm, condition in enumerate(CONDITIONS):
                block = slice(number*12+arm*4, number*12+arm*4+4)
                values = z[condition+'_arrivals_mV']
                assert values.shape == (60000, 4) and np.isfinite(values).all()
                for j in range(4):
                    weights = dense[j]
                    if condition == 'pn_dm1_only' and j < 2: weights = weights*masks[0]
                    if condition == 'dna_without_aotu019' and j >= 2: weights = weights*masks[1]
                    # Direct weighted event accumulation; no CSR, partition or
                    # delayed_impulses helper and no observed refractory gate.
                    independently_summed = np.bincount(arrivals, weights=weights[events], minlength=60000)
                    error = float(np.max(abs(independently_summed-values[:, j])))
                    maximum_drive_error = max(maximum_drive_error, error)
                    assert error <= 1e-10, (name, condition, j, error)
                drive[:, block] = values
                record = records[name, condition]; path = OUT/record['file']; assert sha(path) == record['sha256']
                with np.load(path) as replay:
                    ticks = replay['spike_ticks']; indices = replay['spike_i']
                    assert ((ticks >= 0) & (ticks < 60000)).all() and ((indices >= 0) & (indices < 4)).all()
                    assert np.unique(ticks*4+indices).size == len(ticks)
                    expected_spikes[ticks, block.start+indices] = True
                    counts = np.zeros((240, 4), np.int64); np.add.at(counts, (ticks//250, indices), 1)
                    np.testing.assert_array_equal(counts, replay['counts_25ms'])
                    assert not replay['adapt_mV'].any()
                    expected_counts[:, block] = counts
                    for key in expected_state: expected_state[key][:, block] = replay[key]
                    model, cue, seed = name.rsplit('-', 2)
                    traces[model, condition, int(seed), cue] = counts/.025
                    if condition == 'intact':
                        for j, target in enumerate(targets):
                            np.testing.assert_array_equal(ticks[indices == j], tt[ii == target])
        del ii, tt, events, arrivals; gc.collect()
        print('Direct graph/event audit', number+1, '/28', name, flush=True)

    # Exact analytical update of the stated two-variable linear differential
    # equation. Schedule: integrate eligible units, threshold, gated arrivals,
    # reset, end-of-step sample. Refractory gates follow predicted spikes.
    ev = np.exp(-.0001/.020); eg = np.exp(-.0001/.005)
    coupling = .005/(.020-.005)*(ev-eg)
    voltage = np.full(336, -52.); conductance = np.zeros(336)
    last_spike = np.full(336, -10**9, np.int64)
    counts = np.zeros_like(expected_counts); exact = True
    errors = {'v_mV': 0., 'g_mV': 0.}
    for tick in range(60000):
        eligible = tick-last_spike >= 22
        voltage[eligible] = -52+(voltage[eligible]+52)*ev+conductance[eligible]*coupling
        conductance[eligible] *= eg
        spikes = eligible & (voltage > -45)
        if not np.array_equal(spikes, expected_spikes[tick]):
            raise AssertionError(('Independent threshold mismatch', tick, np.flatnonzero(spikes != expected_spikes[tick]).tolist()))
        conductance[eligible & ~spikes] += drive[tick, eligible & ~spikes]
        voltage[spikes] = -52; conductance[spikes] = 0; last_spike[spikes] = tick
        counts[tick//250] += spikes
        if tick % 250 == 249:
            for key, value in [('v_mV', voltage), ('g_mV', conductance)]:
                errors[key] = max(errors[key], float(np.max(abs(value-expected_state[key][tick//250]))))
    np.testing.assert_array_equal(counts, expected_counts)
    assert max(errors.values()) <= 1e-10, errors

    scalar_checks = 0
    for family in ['contrast', 'gradient']:
        for row in r[family]:
            col = 0 if row['readout'] == 'PN' else 2
            lo, hi = p['pulse_windows'][row['pulse']-1]
            keys = ['a_left', 'a_right', 'none'] if family == 'contrast' else ['g60', 'g40', 'equal']
            values = []
            for cue in keys:
                rates = traces[row['parent_model'], row['condition'], row['seed'], cue]
                values.append(float((rates[lo:hi, col]-rates[lo:hi, col+1]).sum()/(hi-lo)))
            left, right, neutral = values
            minimum = p['gates'][('multi_trial_contrast_hz' if family == 'contrast' else 'gradient_contrast_hz')
                                 if col == 0 else ('motor_direction_contrast_hz' if family == 'contrast' else 'motor_gradient_contrast_hz')]
            criterion = left-right >= minimum and left > neutral and right < neutral
            fields = ['left', 'right', 'none'] if family == 'contrast' else ['g60', 'g40', 'equal']
            assert all(row[key] == value for key, value in zip(fields, values))
            assert row['separation_hz'] == left-right and row['criterion_satisfied'] == criterion
            scalar_checks += 1
    recovery_checks = 0
    for row in r['receiver_recovery']:
        lo, hi = p['recovery_windows'][row['pulse']-1]
        trial = traces[row['parent_model'], row['condition'], row['seed'], row['cue']]
        neutral = traces[row['parent_model'], row['condition'], row['seed'], 'none']
        delta = trial[lo:hi].sum(0)/(hi-lo)-neutral[lo:hi].sum(0)/(hi-lo)
        assert row['individual_PN_difference_hz'] == delta[:2].tolist()
        assert row['signed_DNa02_difference_hz'] == float(delta[2]-delta[3])
        assert row['receiver_PN_recovery_bound_satisfied'] == bool(max(abs(delta[:2])) <= 5)
        assert row['receiver_signed_DNa02_recovery_bound_satisfied'] == bool(abs(delta[2]-delta[3]) <= 5)
        recovery_checks += 1
    assert all(sha(ROOT/key) == value for key, value in p['source_hashes'].items())
    atomic_json(OUT/'independent-audit.json', dict(status='passed', source_sha256=sha(Path(__file__)),
        protocol_sha256=sha(OUT/'protocol.json'), chunks_rehashed=chunks, input_files_rehashed=28,
        native_replays_rehashed=84, direct_event_drive_arrays_checked=336, maximum_arrival_error_mV=maximum_drive_error,
        independently_predicted_receiver_units=336, threshold_spike_ticks_exact=True, counts_exact=True,
        maximum_closed_form_state_error_mV=errors, scalar_direction_gradient_checks=scalar_checks,
        recovery_checks=recovery_checks, sources_reverified=True, full_brain_runs=0, controller_changed=False,
        method='Direct dense graph/event bincount; closed-form linear integration and new threshold/refractory/reset decisions; independent scalar bounds. No Brian2 or analyzer helper imports.',
        wall_seconds=time.monotonic()-started, peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print('Independent event and closed-form audit passed', errors, flush=True)


if __name__ == '__main__': main()

"""Post-run descriptive domain engagement, not a new acceptance gate."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from flygarden.continuous_candidate import file_sha
from flygarden.recording import atomic_json

OUT = ROOT/'reports/brain-integration/recovery/recovered-mbon32-capability-v1'


def main():
    p = json.loads((OUT/'protocol.json').read_text()); records = []; streams = {}
    targets = [p['mapping'][key][0]['index'] for key in ['DNa02_left', 'DNa02_right']]
    for seed in p['diagnostic_seeds']:
        for case in p['cases']:
            folder = OUT/'trials'/f'{case}-{seed}'; m = json.loads((folder/'manifest.json').read_text())
            total = np.zeros(138639, np.int64); recorded_total = total.copy(); trains = [[], []]
            for chunk in m['chunks']:
                path = folder/chunk['file']; assert file_sha(path) == chunk['sha256']
                with np.load(path) as z:
                    total += np.bincount(z['spike_i'], minlength=138639); recorded_total += z['counts']
                    for j, target in enumerate(targets):
                        trains[j].extend(np.rint(z['spike_t'][z['spike_i'] == target]/.0001).astype(np.int64).tolist())
            np.testing.assert_array_equal(total, recorded_total)
            records.append(dict(seed=seed, case=case, active_full_network_neurons=int((total > 0).sum()),
                total_spikes=int(total.sum()), adapted_domain_spikes=int(total[p['domain']['indices']].sum()),
                adapted_domain_active_neurons=int((total[p['domain']['indices']] > 0).sum())))
            streams[seed, case] = trains
        with np.load(OUT/'trials'/f'left-{seed}'/'continuation-state.npz') as z:
            assert not z['adapt'].any(), 'Nonzero adaptation despite the observed silent domain'
    differences = [dict(seed=seed, case=case, DNa02_left_spike_ticks_identical_to_none=streams[seed, case][0] == streams[seed, 'none'][0],
                        DNa02_right_spike_ticks_identical_to_none=streams[seed, case][1] == streams[seed, 'none'][1])
                   for seed in p['diagnostic_seeds'] for case in ['left', 'right', 'both']]
    atomic_json(OUT/'activity-coverage.json', dict(scope='Post-run descriptive raw-event/domain engagement; not preregistered or a new acceptance gate.',
        records=records, spike_timing_comparisons=differences, full_continuation_adaptation_arrays_zero=True,
        raw_events_and_monitor_counts_exact=True, protocol_sha256=file_sha(OUT/'protocol.json'), source_sha256=file_sha(Path(__file__)),
        inference='The395-cell adaptation mechanism never receives a spike increment in this odor-free screen. No conclusion about active olfactory adaptation follows.',
        criterion_values_changed=False, new_full_brain_runs=0))


if __name__ == '__main__': main()

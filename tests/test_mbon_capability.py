import numpy as np
import pytest

from flygarden.mbon_capability import drive_events, drive_rates, evaluate_capability


def test_two_pulse_boundaries_and_no_odor_control():
    for tick in [0, 11, 32, 100, 131, 152, 220, 239]:
        assert not drive_rates('both', tick).any()
    for tick in [12, 31, 132, 151]:
        np.testing.assert_array_equal(drive_rates('left', tick), [50, 0])
        np.testing.assert_array_equal(drive_rates('right', tick), [0, 50])
        assert not drive_rates('none', tick).any()
    with pytest.raises(ValueError): drive_rates('left', 240)


def test_matched_source_trains_and_rng_restart():
    rngs = {case: np.random.default_rng(22401) for case in ['left', 'right', 'both', 'none']}
    for tick in range(240):
        events = {case: drive_events(rng, case, tick) for case, rng in rngs.items()}
        for case, side in [('left', 0), ('right', 1)]:
            ii, tt = events[case]; bi, bt = events['both']
            np.testing.assert_array_equal(tt[ii == side], bt[bi == side])
        if tick == 150:
            restored = np.random.default_rng(); restored.bit_generator.state = rngs['both'].bit_generator.state
        if tick == 151:
            ri, rt = drive_events(restored, 'both', tick)
            np.testing.assert_array_equal(ri, events['both'][0]); np.testing.assert_array_equal(rt, events['both'][1])


def fixture():
    p = dict(diagnostic_seeds=[12401, 12402], burst_windows=[[44, 132], [164, 240]])
    traces = {(s, c): np.zeros((240, 12)) for s in p['diagnostic_seeds'] for c in ['none', 'left', 'right', 'both']}
    for t in traces.values(): t[:, 4:6] = 65
    return p, traces


def test_same_side_motor_bias_fails_despite_stimulated_cells_responding():
    p, traces = fixture()
    for (seed, case), t in traces.items():
        if case == 'none': continue
        sides = [0] if case == 'left' else [1] if case == 'right' else [0, 1]
        for lo, hi in [(12, 32), (132, 152)]:
            t[lo:hi, sides] = 50; t[lo:hi, 2] = 20
    r = evaluate_capability(p, traces)
    assert all(x['passed'] for x in r['responses'])
    assert not any(x['passed'] for x in r['direction']) and not r['capability_neural_checks_passed']
    assert not r['controller_promoted']


def test_repeated_opponent_response_can_pass_but_persistent_activity_fails():
    p, traces = fixture()
    for (seed, case), t in traces.items():
        if case == 'none': continue
        sides = [0] if case == 'left' else [1] if case == 'right' else [0, 1]
        for lo, hi in [(12, 32), (132, 152)]:
            t[lo:hi, sides] = 50
            for side in sides: t[lo:hi, 2+side] = 20
    assert evaluate_capability(p, traces)['capability_neural_checks_passed']
    traces[12401, 'right'][220:240, 1] = 20
    assert not evaluate_capability(p, traces)['capability_neural_checks_passed']


def test_missing_trials_and_invalid_activity_cannot_pass():
    p, traces = fixture(); traces.pop((12401, 'none'))
    with pytest.raises(ValueError): evaluate_capability(p, traces)
    p, traces = fixture(); traces[12401, 'none'][0, 2] = np.nan
    with pytest.raises(ValueError): evaluate_capability(p, traces)

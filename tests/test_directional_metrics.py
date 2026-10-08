"""Failure cases that must not be disguised by averaging or magnitude alone."""
import numpy as np
import pytest
from flygarden.directional_metrics import opponent, gradient, evaluate_traces


def fixture():
    protocol = {'models': ['original', 'local_adaptive'], 'validation_seeds': [12301],
                'cues': ['none', 'a_left', 'a_right', 'a_both', 'equal', 'g60', 'g40'],
                'pulse_windows': [[12, 32], [132, 152]], 'recovery_windows': [[100, 120], [220, 240]],
                'burst_windows': [[44, 132], [164, 240]],
                'gates': {'response_gain_hz': 10, 'individual_PN_and_local_recovery_difference_hz': 5,
                          'signed_DNa02_recovery_difference_hz': 5, 'walking_support_retention_fraction': .8,
                          'burst_100ms_recovery_PN_difference_hz': 20, 'multi_trial_contrast_hz': 10,
                          'gradient_contrast_hz': 5, 'motor_direction_contrast_hz': 10,
                          'motor_gradient_contrast_hz': 5}}
    traces = {}
    for model in protocol['models']:
        for cue in protocol['cues']:
            t = np.zeros((240, 10));t[:, 4:6] = 65
            if cue != 'none':
                diff = {'a_left': 20, 'a_right': -20, 'a_both': 0, 'equal': 0, 'g60': 5, 'g40': -5}[cue]
                for lo, hi in protocol['pulse_windows']:
                    t[lo:hi, :4] = [50 + diff / 2, 50 - diff / 2, 50 + diff / 2, 50 - diff / 2]
            traces[(model, 12301, cue)] = t
    return protocol, traces


def test_ordered_same_side_responses_fail_opponent_gate():
    assert not opponent(50, 20, 0, 10)['passed']
    assert opponent(10, -10, 0, 10)['passed']


def test_binary_response_without_gradient_fails():
    assert not gradient(30, 30, 30, 5)['passed']
    assert not gradient(30, 20, 10, 5)['passed']
    assert gradient(12.5, 7.5, 10, 5)['passed']


def test_individual_recovery_prevents_cross_neuron_cancellation():
    p, t = fixture()
    for key in t: t[key][100:120, :2] = [10, 10]
    t[('local_adaptive', 12301, 'a_left')][100:120, :2] = [20, 0]
    result = evaluate_traces(p, t)
    record = next(r for r in result['recovery'] if r['model'] == 'local_adaptive' and r['cue'] == 'a_left' and r['pulse'] == 1)
    assert record['pn_recovery_difference_hz'] == [10, -10]
    assert not record['PN_recovery_passed']


def test_late_burst_is_not_hidden_by_final_recovery():
    p, t = fixture();t[('local_adaptive', 12301, 'a_left')][60:64, :2] = 30
    result = evaluate_traces(p, t)
    assert not result['bursts'][12]['passed']
    record = next(r for r in result['recovery'] if r['model'] == 'local_adaptive' and r['cue'] == 'a_left' and r['pulse'] == 1)
    assert record['PN_recovery_passed']


def test_motor_alignment_cannot_replace_primary_pn_gate():
    p, t = fixture();t[('local_adaptive', 12301, 'a_right')][12:32, :2] = [65, 35]
    result = evaluate_traces(p, t)
    assert result['motor_alignment_passed']['local_adaptive']
    assert not result['primary_neural_gates_passed']['local_adaptive']


def test_incomplete_trial_set_rejected():
    p, t = fixture();t.pop(('local_adaptive', 12301, 'g40'))
    with pytest.raises(ValueError, match='Incomplete'):evaluate_traces(p, t)

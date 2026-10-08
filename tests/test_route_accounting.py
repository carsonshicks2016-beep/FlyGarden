import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flygarden.route_accounting import phase_delivery, signed_totals
from flygarden.feedback_trace import refractory_gate


def test_arrival_clock_half_open_phase_and_refractory_release():
    # Delayed arrivals at 20, 21, 22 and 23. Phase [21, 23) keeps 21/22;
    # target's spike at 20 rejects tick 21 and releases exactly at tick 22.
    gate = refractory_gate([20], 30, refractory_ticks=2)
    ids, before, after = phase_delivery([0, 1, 0, 1], [18, 19, 20, 21],
                                        csr_matrix([[2., -3.]]), gate,
                                        21, 23, dt_s=.001, delay_ticks=2)
    np.testing.assert_array_equal(ids, [0, 1])
    np.testing.assert_array_equal(before, [1000., -1500.])
    np.testing.assert_array_equal(after, [1000., 0.])


def test_opposing_delivery_is_not_erased_by_net_cancellation():
    _, before, after = phase_delivery([0, 1], [0, 0], csr_matrix([[2., -2.]]),
                                      np.ones(10, bool), 0, 10,
                                      dt_s=.001, delay_ticks=0)
    np.testing.assert_array_equal(before, after)
    assert signed_totals(after) == dict(positive_mV_per_s=200.,
                                        negative_mV_per_s=200., net_mV_per_s=0.)


def test_spike_tick_is_erased_and_zero_weight_remains_zero():
    gate = refractory_gate([5], 30, refractory_ticks=22)
    _, before, after = phase_delivery([0, 1, 0], [5, 5, 27],
                                      csr_matrix([[3., 0.]]), gate, 0, 30,
                                      dt_s=.001, delay_ticks=0)
    assert before.sum() == 200. and after.sum() == 100.


def test_out_of_range_phase_and_source_are_rejected():
    row = csr_matrix([[1.]])
    with pytest.raises(ValueError):
        phase_delivery([1], [0], row, np.ones(10, bool), 0, 10)
    with pytest.raises(ValueError):
        phase_delivery([0], [0], row, np.ones(10, bool), 0, 11)

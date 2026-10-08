import json
import numpy as np
import pytest
from flygarden.route_state_audit import edge_delivery, timing_difference, json_native


def test_arrival_phase_reset_and_exact_refractory_release():
    # Source ticks 2,3,23,24 arrive 20,21,41,42. A target spike at 20
    # rejects through 41 and releases at 42; [20,43) is half-open.
    r=edge_delivery([2,3,23,24,25], [20], -2.75, 20,43)
    assert (r['arrivals'],r['accepted'],r['rejected'])==(4,1,3)
    assert r['accepted_mV_per_s']==-2.75/(23*.0001)


def test_repeated_source_events_and_negative_sign_are_preserved():
    r=edge_delivery([0,0,1], [], -11., 18,20)
    assert r['accepted']==r['arrivals']==3 and r['accepted_mV_per_s']<0


def test_equal_counts_do_not_imply_equal_timing():
    r=timing_difference([10,20,30], [10,21,31])
    assert r['count_delta']==0 and r['event_disagreements']==4
    assert r['equal_counts_different_ticks'] and r['shared_ticks']==1
    assert r['symmetric_nearest_event_max_ms']==.1


def test_added_deleted_spikes_and_empty_sets():
    r=timing_difference([5,10], [10])
    assert r['count_delta']==-1 and r['event_disagreements']==1
    assert timing_difference([],[])['exact_ticks_equal']
    assert timing_difference([],[1])['symmetric_nearest_event_median_ms'] is None


def test_unsorted_targets_and_duplicate_neuron_ticks_rejected():
    with pytest.raises(ValueError):edge_delivery([1],[5,2],1,0,10)
    with pytest.raises(ValueError):timing_difference([1,1],[1])


def test_scalar_codec_keeps_false_and_values():
    r=json.loads(json.dumps(json_native({'criterion':np.bool_(False),'n':np.int64(2),'v':np.float64(.25)})))
    assert r=={'criterion':False,'n':2,'v':.25}

"""Recorded-event diagnostics. Never constructs or changes a brain controller."""
import numpy as np


def edge_delivery(source_ticks, target_ticks, weight_mv, lo, hi, *, delay=18, refractory=22, dt=.0001):
    """Attribution by arrival clock; observed gates are not predictive gates.

    A reset erases synaptic delivery on the threshold/spike tick. The following
    ticks are rejected until the 2.2 ms refractory interval releases at tick 22.
    This helper is restricted to the two unchanged DNa02 recipients.
    """
    source = np.asarray(source_ticks, dtype=np.int64)
    target = np.asarray(target_ticks, dtype=np.int64)
    if not 0 <= lo < hi or dt <= 0 or delay < 0 or refractory <= 0:
        raise ValueError('Invalid phase or recipient timing')
    if np.any(np.diff(target) < 0) or np.any(source < 0) or np.any(target < 0):
        raise ValueError('Invalid spike clock')
    arrivals = source + delay
    arrivals = arrivals[(arrivals >= lo) & (arrivals < hi)]
    last = np.searchsorted(target, arrivals, side='right') - 1
    eligible = np.ones(len(arrivals), bool)
    valid = last >= 0
    eligible[valid] = arrivals[valid] - target[last[valid]] >= refractory
    before = len(arrivals); accepted = int(eligible.sum())
    duration = (hi-lo)*dt
    return dict(arrivals=before, accepted=accepted, rejected=before-accepted,
                before_mV_per_s=float(before*weight_mv/duration),
                accepted_mV_per_s=float(accepted*weight_mv/duration))


def timing_difference(reference, changed):
    """Exact event disagreement, plus explicitly non-correspondence distances.

    Nearest-event distances do not identify a shifted individual spike: spikes
    may appear/disappear. Empty sets have no defined nearest-event distance.
    """
    a = np.asarray(reference, dtype=np.int64); b = np.asarray(changed, dtype=np.int64)
    if np.unique(a).size != len(a) or np.unique(b).size != len(b):
        raise ValueError('Duplicate single-neuron spike ticks')
    shared = int(np.intersect1d(a, b).size)
    distances = []
    if len(a) and len(b):
        a = np.sort(a); b = np.sort(b)
        for x, y in [(a, b), (b, a)]:
            j = np.searchsorted(y, x)
            distances.extend(np.minimum(abs(x-y[np.maximum(j-1, 0)]),
                                        abs(x-y[np.minimum(j, len(y)-1)])).tolist())
    return dict(reference_count=len(a), changed_count=len(b), shared_ticks=shared,
                event_disagreements=len(a)+len(b)-2*shared,
                count_delta=len(b)-len(a), exact_ticks_equal=bool(np.array_equal(np.sort(a), np.sort(b))),
                equal_counts_different_ticks=bool(len(a)==len(b) and shared!=len(a)),
                symmetric_nearest_event_median_ms=float(np.median(distances)*.1) if distances else None,
                symmetric_nearest_event_max_ms=float(max(distances)*.1) if distances else None)


def json_native(value):
    """Convert NumPy scalar types only; keep failed scientific criteria intact."""
    if isinstance(value, dict):return {key:json_native(item) for key,item in value.items()}
    if isinstance(value, (list, tuple)):return [json_native(item) for item in value]
    if isinstance(value, np.generic):return value.item()
    return value

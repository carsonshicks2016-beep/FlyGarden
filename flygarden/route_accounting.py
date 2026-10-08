"""Descriptive signed delivery from recorded events; no controller or fitting."""
import numpy as np


def phase_delivery(indices, ticks, row, gate, lo, hi, dt_s=.0001, delay_ticks=18):
    """Return source-indexed pre-gate and accepted increments, in mV/s.

    Phases use arrival time, not source spike time. A gate is derived from the
    observed target spikes, including reset-erased arrivals on the spike tick.
    Opposing sources remain separate even when their net delivery cancels.
    """
    indices = np.asarray(indices, dtype=int)
    ticks = np.asarray(ticks, dtype=int)
    gate = np.asarray(gate, dtype=bool)
    if (indices.ndim != 1 or ticks.shape != indices.shape or row.shape[0] != 1
            or gate.ndim != 1 or not 0 <= lo < hi <= len(gate) or dt_s <= 0
            or delay_ticks < 0 or np.any(indices < 0)
            or np.any(indices >= row.shape[1])):
        raise ValueError('Invalid event attribution inputs')
    arrivals = ticks + delay_ticks
    mask = (arrivals >= lo) & (arrivals < hi)
    sources, times = indices[mask], arrivals[mask]
    all_counts = np.bincount(sources, minlength=row.shape[1])
    accepted_counts = np.bincount(sources[gate[times]], minlength=row.shape[1])
    row = row.tocsr(copy=True);row.sum_duplicates();row.sort_indices()
    duration = (hi - lo) * dt_s
    return (row.indices.copy(), all_counts[row.indices] * row.data / duration,
            accepted_counts[row.indices] * row.data / duration)


def signed_totals(values):
    """Positive/negative magnitudes and their signed net, without cancellation."""
    values = np.asarray(values, dtype=float)
    if not np.isfinite(values).all():raise ValueError('Nonfinite delivery')
    positive = float(values[values > 0].sum())
    negative = float(-values[values < 0].sum())
    return dict(positive_mV_per_s=positive, negative_mV_per_s=negative,
                net_mV_per_s=positive - negative)

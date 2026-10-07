"""Offline accounting of recorded drive, in voltage-equivalent millivolts.

Observed spikes determine refractory/reset timing. This reconstructs g and
adapt; it does not independently predict voltage, spikes, or causal effects.
"""
import numpy as np


def replay_recorded_states(arrivals_mv, spikes, step_mv, tau_s=.45,
                           dt_s=.0001, refractory_ticks=22, sample_ticks=250):
    arrivals = np.asarray(arrivals_mv, dtype=float)
    spikes = np.asarray(spikes, dtype=bool)
    step = np.asarray(step_mv, dtype=float)
    if (arrivals.ndim != 2 or spikes.shape != arrivals.shape or
            step.shape != (arrivals.shape[1],) or not np.isfinite(arrivals).all() or
            not np.isfinite(step).all() or np.any(step < 0) or
            tau_s <= 0 or dt_s <= 0 or refractory_ticks < 0 or sample_ticks < 1):
        raise ValueError('Invalid replay inputs')
    n = arrivals.shape[1]
    g = np.zeros(n); adapt = np.zeros(n)
    last = np.full(n, -10**9, dtype=np.int64)
    gd = np.exp(-dt_s/.005); ad = np.exp(-dt_s/tau_s)
    gs = []; ads = []; gates = np.zeros_like(spikes)
    for tick in range(len(arrivals)):
        available = tick-last >= refractory_ticks
        g[available] *= gd
        adapt *= ad
        # Arrivals on a spike tick are erased by reset. Treat them as rejected
        # in the accounting gate, matching the stored before-synapse gate.
        accepted = available & ~spikes[tick]
        gates[tick] = accepted
        g[accepted] += arrivals[tick, accepted]
        g[spikes[tick]] = 0
        adapt[spikes[tick]] += step[spikes[tick]]
        last[spikes[tick]] = tick
        if (tick+1) % sample_ticks == 0:
            gs.append(g.copy()); ads.append(adapt.copy())
    return np.asarray(gs), np.asarray(ads), gates

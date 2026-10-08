"""Fixed direct-MBON32 diagnostic schedule and neural-only measurements."""
import numpy as np

CASES = ('none', 'left', 'right', 'both')
PULSES = ((12, 32), (132, 152))
RECOVERY = ((100, 120), (220, 240))


def drive_rates(case, tick):
    if case not in CASES or not isinstance(tick, (int, np.integer)) or not 0 <= tick < 240:
        raise ValueError('Fixed six-second capability case/window required')
    active = any(lo <= tick < hi for lo, hi in PULSES)
    return np.array([50. if active and case in ('left', 'both') else 0.,
                     50. if active and case in ('right', 'both') else 0.])


def drive_events(rng, case, tick):
    # Draw both channels even when inactive, preserving matched random sources.
    offsets, indices = np.nonzero(rng.random((250, 2)) < drive_rates(case, tick)*.0001)
    return indices.astype(np.int32), (tick*250+offsets)*.0001


def evaluate_capability(protocol, traces):
    """Traces are 240 x 12 Hz: MBON L/R, DNA L/R, support L/R, PN L/R, four locals."""
    seeds = protocol['diagnostic_seeds']
    if set(traces) != {(seed, case) for seed in seeds for case in CASES}:
        raise ValueError('Complete eight-trial capability set required')
    if any(t.shape != (240, 12) or not np.isfinite(t).all() or (t < 0).any() for t in traces.values()):
        raise ValueError('Finite nonnegative twelve-population traces required')
    direction = []; responses = []; recoveries = []; support = []; bursts = []
    for seed in seeds:
        none = traces[seed, 'none']
        for pulse, ((pl, ph), (rl, rh)) in enumerate(zip(PULSES, RECOVERY), 1):
            contrast = {case: float((traces[seed, case][pl:ph, 2]-traces[seed, case][pl:ph, 3]).mean())
                        for case in CASES}
            delta = {case: contrast[case]-contrast['none'] for case in CASES[1:]}
            flags = {'left_delta_at_least_5Hz': delta['left'] >= 5,
                     'right_delta_at_most_minus_5Hz': delta['right'] <= -5,
                     'bilateral_delta_within_5Hz': abs(delta['both']) <= 5,
                     'existing_descending_opponent_bound': contrast['left']-contrast['right'] >= 10 and
                          contrast['left'] > contrast['none'] and contrast['right'] < contrast['none']}
            direction.append(dict(seed=seed, pulse=pulse, contrast_hz=contrast, delta_from_none_hz=delta,
                                  separation_hz=contrast['left']-contrast['right'], **flags, passed=bool(all(flags.values()))))
            for case in CASES[1:]:
                t = traces[seed, case]
                active = [0] if case == 'left' else [1] if case == 'right' else [0, 1]
                gains = t[pl:ph, active].mean(0)-none[pl:ph, active].mean(0)
                previous = none[pl:ph, active].mean(0) if pulse == 1 else t[100:120, active].mean(0)
                renewed = t[pl:ph, active].mean(0)-previous
                responses.append(dict(seed=seed, case=case, pulse=pulse, stimulated_sides=active,
                    matched_control_gain_hz=gains.tolist(), gain_from_previous_recovery_hz=renewed.tolist(),
                    passed=bool(np.all(gains >= 10) and np.all(renewed >= 10))))
                difference = t[rl:rh].mean(0)-none[rl:rh].mean(0)
                flags = {'MBON_recovery_passed': bool(max(abs(difference[:2])) <= 5),
                         'PN_local_recovery_passed': bool(max(abs(difference[6:])) <= 5),
                         'signed_DNa02_recovery_passed': abs(difference[2]-difference[3]) <= 5}
                recoveries.append(dict(seed=seed, case=case, pulse=pulse, individual_difference_hz=difference.tolist(),
                                       **flags, passed=bool(all(flags.values()))))
                for phase, lo, hi in [('pulse', pl, ph), ('recovery', rl, rh)]:
                    reference = none[lo:hi, 4:6].mean(0); actual = t[lo:hi, 4:6].mean(0)
                    support.append(dict(seed=seed, case=case, pulse=pulse, phase=phase,
                        matched_candidate_none_hz=reference.tolist(), actual_hz=actual.tolist(),
                        passed=bool(np.all(reference > 0) and np.all(actual >= .8*reference))))
        for case in CASES[1:]:
            excess = traces[seed, case]-none
            for lo, hi in protocol['burst_windows']:
                mbon = [max(float(excess[i:i+4, side].mean()) for i in range(lo, hi-3)) for side in [0, 1]]
                pn = max(float(excess[i:i+4, 6:8].mean()) for i in range(lo, hi-3))
                bursts.append(dict(seed=seed, case=case, window=[lo, hi], MBON_100ms_excess_hz=mbon,
                                   PN_100ms_excess_hz=pn, passed=bool(max(mbon) <= 20 and pn <= 20)))
    families = dict(direction=direction, responses=responses, recovery=recoveries, support_perturbation=support, bursts=bursts)
    return dict(status='complete', **families, capability_neural_checks_passed=all(x['passed'] for rows in families.values() for x in rows),
                production_controller_changed=False, controller_promoted=False, navigation_validated=False, learning_validated=False,
                original_PN_gate3_and_gate6_retested=False, acceptance_criteria_changed=False)

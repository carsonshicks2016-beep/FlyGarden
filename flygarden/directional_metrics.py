"""Prospective neural-screen metrics, preserving the earlier PN gate rules.

No fitted baseline subtraction or output normalization. Motor metrics are
reported separately from the original PN criteria and cannot replace them.
"""
import numpy as np


def opponent(left, right, neutral, minimum):
    """An ordered pair alone is insufficient: the signals must bracket neutral."""
    return {'left': float(left), 'right': float(right), 'none': float(neutral),
            'separation_hz': float(left - right),
            'passed': bool(left - right >= minimum and left - neutral > 0 and right - neutral < 0)}


def gradient(g60, g40, equal, minimum):
    return {'g60': float(g60), 'g40': float(g40), 'equal': float(equal),
            'separation_hz': float(g60 - g40),
            'passed': bool(g60 - g40 >= minimum and g60 - equal > 0 and g40 - equal < 0)}


def evaluate_traces(protocol, traces):
    """Read 240x10 Hz traces: PN L/R, DNa02 L/R, DNp09 L/R, four locals."""
    models, seeds, cues = protocol['models'], protocol['validation_seeds'], protocol['cues']
    required = {(m, s, c) for m in models for s in seeds for c in cues}
    if set(traces) != required:
        raise ValueError('Incomplete or unexpected trial set')
    if any(t.shape != (240, 10) or not np.isfinite(t).all() or (t < 0).any() for t in traces.values()):
        raise ValueError('Finite nonnegative 240x10 neural rates required')
    gates = protocol['gates']
    recovery, bursts, support, contrast, gradients, motor_contrast, motor_gradient = ([] for _ in range(7))
    for model in models:
        for seed in seeds:
            none = traces[(model, seed, 'none')]
            original_none = traces[('original', seed, 'none')]
            support.append({'model': model, 'seed': seed,
                            'rate_hz': none[:, 4:6].mean(0).tolist(),
                            'reference_rate_hz': original_none[:, 4:6].mean(0).tolist(),
                            'passed': bool(np.all(none[:, 4:6].mean(0) >=
                                                 gates['walking_support_retention_fraction'] * original_none[:, 4:6].mean(0)))})
            for cue in [c for c in cues if c != 'none']:
                trial = traces[(model, seed, cue)]
                pn, neutral = trial[:, :2].mean(1), none[:, :2].mean(1)
                for pulse, (pl, ph), (rl, rh) in zip([1, 2], protocol['pulse_windows'], protocol['recovery_windows']):
                    baseline = neutral[pl:ph].mean() if pulse == 1 else pn[100:120].mean()
                    gain = float(pn[pl:ph].mean() - baseline)
                    pn_diff = trial[rl:rh, :2].mean(0) - none[rl:rh, :2].mean(0)
                    local_diff = trial[rl:rh, 6:].mean(0) - none[rl:rh, 6:].mean(0)
                    dna = float((trial[:, 2] - trial[:, 3] - none[:, 2] + none[:, 3])[rl:rh].mean())
                    flags = {'response_passed': gain >= gates['response_gain_hz'],
                             'PN_recovery_passed': bool(max(abs(pn_diff)) <= gates['individual_PN_and_local_recovery_difference_hz']),
                             'local_recovery_passed': bool(max(abs(local_diff)) <= gates['individual_PN_and_local_recovery_difference_hz']),
                             'DNa02_recovery_passed': abs(dna) <= gates['signed_DNa02_recovery_difference_hz']}
                    recovery.append({'model': model, 'seed': seed, 'cue': cue, 'pulse': pulse,
                                     'gain_hz': gain, 'pn_recovery_difference_hz': pn_diff.tolist(),
                                     'local_recovery_difference_hz': local_diff.tolist(),
                                     'signed_dna_recovery_difference_hz': dna,
                                     **flags, 'passed': bool(all(flags.values()))})
                for lo, hi in protocol['burst_windows']:
                    excess = pn - neutral
                    maximum = max(float(excess[i:i + 4].mean()) for i in range(lo, hi - 3))
                    bursts.append({'model': model, 'seed': seed, 'cue': cue, 'window': [lo, hi],
                                   'max_100ms_PN_excess_hz': maximum,
                                   'passed': maximum <= gates['burst_100ms_recovery_PN_difference_hz']})
            for pulse, (lo, hi) in enumerate(protocol['pulse_windows'], 1):
                def difference(cue, column):
                    t = traces[(model, seed, cue)]
                    return float((t[lo:hi, column] - t[lo:hi, column + 1]).mean())
                identity = {'model': model, 'seed': seed, 'pulse': pulse}
                contrast.append({**identity, **opponent(difference('a_left', 0), difference('a_right', 0),
                                                       difference('none', 0), gates['multi_trial_contrast_hz'])})
                gradients.append({**identity, **gradient(difference('g60', 0), difference('g40', 0),
                                                        difference('equal', 0), gates['gradient_contrast_hz'])})
                motor_contrast.append({**identity, **opponent(difference('a_left', 2), difference('a_right', 2),
                                                             difference('none', 2), gates['motor_direction_contrast_hz'])})
                motor_gradient.append({**identity, **gradient(difference('g60', 2), difference('g40', 2),
                                                              difference('equal', 2), gates['motor_gradient_contrast_hz'])})
    groups = {'recovery': recovery, 'contrast': contrast, 'bursts': bursts, 'support': support, 'gradient': gradients}
    passed = {model: all(row['passed'] for group in groups.values() for row in group if row['model'] == model)
              for model in models}
    motor = {model: all(row['passed'] for group in [motor_contrast, motor_gradient] for row in group if row['model'] == model)
             for model in models}
    return {'status': 'complete', **groups, 'motor_contrast': motor_contrast, 'motor_gradient': motor_gradient,
            'primary_neural_gates_passed': passed, 'motor_alignment_passed': motor,
            'controller_promoted': False, 'embodied_qualification': False, 'learning_qualification': False}

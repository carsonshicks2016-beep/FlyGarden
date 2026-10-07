# Isolated continuous-activity reference results

Evidence review and the small mechanism reference are complete. The application/full-brain controller is unchanged. This is a Python port of the authors’ archived single-glomerulus continuous-rate model, plus an explicitly synthetic two-independent-channel extension. It is not a full connectome run or a fitted electrical cable model.

## Fixed-parameter pulse diagnostics

All conditions use the published parameter vector, an 11-second burn-in, then 0.5-second synthetic pulses at 0.3 and 3.3 seconds. Four variants retain both inhibitory mechanisms, remove local postsynaptic feedback, remove global presynaptic feedback, or remove both. Results below are activity changes relative to each variant’s time-matched unstimulated baseline. They are not measurements from an animal.

| Variant | PN pulse peak gains | Maximum absolute recovery deviations | Within fixed 5-unit recovery tolerance |
| --- | ---: | ---: | --- |
| published | 63.89, 59.61 | 0.88, 1.18 | pass |
| no_post | 69.59, 64.88 | 1.06, 1.42 | pass |
| no_pre | 420.03, 293.82 | 6.28, 6.36 | fail |
| neither | 462.99, 323.80 | 7.55, 7.65 | fail |

The intact published reference responds to both pulses and returns close to baseline, with maximum tail deviations below 1.19 activity units. The model with local feedback removed also passes this tolerance. Therefore this test does **not** show that local feedback alone solves persistence. Removing presynaptic inhibition produces larger positive responses and longer negative aftereffects; those two controls fail the fixed recovery tolerance. Negative baseline-subtracted traces are decreases in nonnegative activity, not negative firing rates.

Synthetic A/B channels preserve an unstimulated channel exactly and mirror exactly. This is a test of an engineered independent-channel construction, not evidence of zero anatomical cross-talk or left/right steering. There are no stochastic seeds, bootstrap intervals, body outcomes or learning claims in this deterministic reference.

## Verification

- Seven tests passed: four independent literal MATLAB-loop comparisons, checkpoint continuation/rejection, atomic input validation and two-pulse zero-background recovery.
- Four fresh-process checkpoints, each continued for 500 samples, reproduce activity exactly with zero maximum error. These are isolated reference checkpoints, not complete brain/body checkpoints.
- Final-state errors against an independent adaptive continuous ODE solver decrease from 0.00514734 at 1 ms, to 0.00210503 at 0.5 ms, to 0.00095842 at 0.25 ms. This supports numerical convergence; native MATLAB/Octave execution was not available and has not been claimed.
- Both authors’ model archive MD5 checksums match their archived metadata. All seven numerical parameters exactly match the archived activity-injection script. Previous full-brain frozen sources were reverified unchanged.
- Comparison plot visually inspected: pulse timing, local versus unaffected channels, positive responses and negative recovery deviations agree with saved traces. Raw traces and all model/control failures are preserved.

Diagnostic runtime: 5.74 seconds. Peak parent-process memory: 149.5 MiB (macOS RSS units; excludes earlier full-brain worker and archive extraction). Detailed source hashes, versions, storage and provenance accompany the result.

## Decision and next stage

The isolated mechanism is numerically checked, but the full-brain recovery and direction gates remain failed. The archived model comments describe LN2P_c and the fit uses DC3 data; our prior sign candidate is twelve lLN2P_b roots and DM1 input. The annotation inventory includes 13 lLN2P_a, 12 lLN2P_b and 9 lLN2P_c neurons. No equivalence is assumed.

Next: resolve exact-root glomerular input/output assignments and rate-to-release units, then write a prospective adapter protocol. The current aggregate connectivity artifact has no individual synapse positions or glomerular assignments. Missing compartment allocation and physiology must remain unavailable rather than being filled with arbitrary channel copies. Consult EVIDENCE.md for the concrete integration prerequisites. Do not install this reference as a substitute navigator or rerun more full-brain sign sweeps.

Reproduce from the project root: `PYTHONPATH=. .venv-next/bin/python scripts/validate_graded_gain_reference.py`; tests: `.venv-next/bin/python -m pytest -q tests/test_graded_gain_reference.py`. The script reads local pinned source files and writes only this diagnostic package. No native brain worker is needed.

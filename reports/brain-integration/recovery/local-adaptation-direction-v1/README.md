# Frozen local-adaptation directional validation

This package follows the successful one-sided recovery screen in local-adaptation-closed-loop-v1. It compares the exact frozen candidate with the original full network on two fresh validation seeds (12301/12302). It is a neural engineering screen; body behavior, navigation, odor B, learning and biological fidelity are outside its scope. No controller is automatically promoted.

The source and protocol were committed and published as `bc0cebc` before execution. The 395-cell local mask, 450 ms decay and 13.5 mV increment are unchanged. PNs and ORNs are not adapted. Every anatomical graph record, original sign, input rule, support setting and motor-decoder coefficient remains fixed; learning is disabled.

## Trial design

Each model/seed receives seven independent six-second trials, for 28 trials total. Neural state resets between trials; every trial presents the same cue twice. The native 0.1 ms neural clock and 25 ms observation windows are retained.

| Case | Left odor A concentration | Right odor A concentration |
|---|---:|---:|
| None | 0 | 0 |
| Left | 1 | 0 |
| Right | 0 | 1 |
| Full bilateral | 1 | 1 |
| Equal | 0.5 | 0.5 |
| 60/40 | 0.6 | 0.4 |
| 40/60 | 0.4 | 0.6 |

Concentration scales the existing 50 Hz maximum per receptor neuron. Equal and unequal cases have the same total concentration; full bilateral is a separate higher-total condition. These are synthetic engineered stimuli, not naturally validated odors or plumes. DNp09 support remains 65 Hz. The controller receives no cue labels or world coordinates.

## Acceptance and interpretation

Response, individual PN/local recovery, signed DNa02 recovery, late bursts, walking support and fresh-process checkpoint continuation retain the previous bounds. Recovery windows are [100,120) and [220,240). The original Gate 3 requires the PN left-minus-right response to bracket the matched no-odor value, with at least 10 Hz separation between left and right trials. Two positive values do not qualify merely because their magnitudes differ.

Gate 6 retains the previous unexecuted gradient evaluator: the 60/40 PN contrast must exceed the equal-input contrast, 40/60 must fall below it, and the unequal pair must differ by at least 5 Hz. Every seed/pulse must pass. DNa02 directional/gradient alignment is separately registered using the same bracketing rules and 10/5 Hz minimum differences. It cannot substitute for failed PN gates. These thresholds are engineering acceptance bounds, not fitted physiological facts or statistical significance claims.

One owned candidate/right-cue worker is deliberately terminated after at least 60 complete chunks. The prefix is retained and hashed. The trial reconstructs from its fixed seed, compares all existing spikes, inputs, selected states and motor commands exactly, then appends the remaining recording. Four left-cue checkpoints also continue in fresh processes, checking five windows and whole neural states.

## Inspection

`protocol.json` is immutable. `progress.json`, `current-worker.json` and `execution.log` are local progress snapshots. Completed `results.json`, `independent-audit.json`, figures and RESULTS.md provide the final evidence. Raw trial chunks and checkpoints remain local; their absence from GitHub prevents independent raw-data reproduction from that snapshot alone.

The offline auditor derives rates from individual spikes, reconstructs the unchanged motor equation and verifies clock, requested rates, input pairing, weights and checkpoint receipts. It also executes the original frozen evaluator in a separate globals dictionary pointed at this package, verifying exact parity for every original primary metric without mutating its module or historical output.

No raw evidence is deleted. The 2 GiB free-space reserve remains enforced; one simulation worker avoids competing full-network allocations. A failed or interrupted package remains inspectable and resumable through its complete chunks.

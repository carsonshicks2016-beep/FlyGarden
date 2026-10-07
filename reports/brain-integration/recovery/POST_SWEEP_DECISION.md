# Decision after the failed adaptive sweep

2026-10-07. The full sweep is complete and no candidate qualifies. The live controller remains unchanged. This decision follows the independent read-only audit and two new bounded diagnostic packages; it authorizes no automatic promotion or altered acceptance gate.

## What the new work established

1. **The cooldown works numerically.** Strong adaptation reduces sustained PN firing substantially. Recorded g/adaptation state replay and six native reconstructions agree with saved states and selected target spikes. These checks found no timing/reset/unit error that explains the continued firing in the tested cases.
2. **The receiving neurons remain driven.** Under the strongest settings, local neurons contribute over 99% of accepted positive increments into the two selected PNs after odor removal. The four monitored locals still fire rapidly and are outside the two strong-sweep adaptation domains. This is descriptive attribution; previous transport-cut experiments provide separate conditional causal evidence.
3. **Persistence and directional readout are distinct problems.** Removing recurrent input in a two-PN replay restores quiet recovery in all tested pulse/recovery comparisons, yet both unilateral cues retain a positive left-minus-right output. The original opponent criterion still fails. Labels identifying neuron side do not establish an opponent functional code.
4. **Some information remains.** Left and right cues differ in response magnitude in these small tests. This does not demonstrate a generalizable decoder or navigation competence. Two calibration seeds cannot establish a biological claim.

Evidence: adaptive-parameter-sweep-v1/RESULTS.md, adaptive-feedback-trace-v1/RESULTS.md, dm1-feedforward-diagnostic-v1/RESULTS.md, and their pinned protocols and machine-readable results.

## Classification of the problems

**Implementation:** No demonstrated numerical defect accounts for the sweep failure. This is bounded evidence, not a proof that the whole application has no bugs. Offline reconstruction uses recorded spikes; the native check independently predicts spikes only for six left-cue recordings and six targets. Full voltage endpoint equality and long-run embodied behavior are outside the new check.

**Evaluation and metadata:** The gates were computed as defined, but a combined response/recovery label hid that almost every setting still responded. The new gate-breakdown.json separates those metrics without changing thresholds. The protocol also retains a stale singular calibration_seed field from the earlier screen; actual execution uses calibration_seeds = [12001,12002] and per-trial seeds. Preserve the original protocol and explain this discrepancy rather than editing a frozen artifact. Threshold constants are duplicated in evaluator source and protocol; they agree now, but future protocol tooling should reject disagreement.

**Scientific assumptions:** A uniform electrical unit, uncertain transmitter classification, compartment allocation, receptor-dependent effects and intrinsic dynamics remain modeling assumptions. Increasing adaptation only in PNs/ORNs does not directly test adaptation in local sources. The earlier 150 ms/1.5 mV broad local/global screen already failed, so simply adding those domains at the same setting is not a new discriminating experiment. Conversely, the strong sweep's failure does not prove local adaptation, graded signaling or other supported mechanisms cannot work.

The chosen two-PN opponent readout is a separate unestablished assumption. Direct anatomical drive favors the selected left PN for both left and right receptor populations; replay preserves that ordering. This is not a demonstrated root-ID swap. Correcting recurrent recovery alone therefore cannot be assumed to satisfy Gate 3.

## Prioritized next work

### 1. Qualify the dominant local sources before changing their dynamics

Use the new exact-root source rankings to select a small representative set. Record transmitter annotation and confidence, cell type, anatomical compartment, measured spiking/graded behavior where published, and target receptor evidence where relevant. Preserve unknowns. Do not infer that all local neurons are inhibitory or that all branches are electrically independent.

Compare the selected roots with the previous sign audit, patchy-cell compartment work and the failed broad adaptation screen. Explain coverage: the four monitored locals are examples, not all remaining recurrent drive. A type-specific candidate needs a defensible mapping and parameter interpretation; engineering-only tests must say so explicitly.

### 2. Test one supported local mechanism with recorded pre-gate input

The new package retains complete incoming signed arrival trains for six targets. Replay these through independently qualified cell dynamics with identical arrival timing, threshold/reset/refractory conventions where appropriate, and a separate registered protocol. Recompute gating after every candidate change. Do not replay previously accepted input as though gates were unchanged.

First compare a reference cell with and without the proposed mechanism, measuring response, late firing, renewed response and parameter units. Include synthetic pulse/off input as well as continuing recorded drive. Continuing input and failure to settle are different questions. Keep AdLIF and local-inhibition mechanisms separate; no unexplained inhibition-gain boost or blanket sign flip.

### 3. Establish what sensory signal the action readout should use

Review primary functional evidence for the exact selected PNs and candidate descending populations. Inspect the wider recorded neural representation descriptively, without selecting a population merely because it maximizes the current two-seed score. Determine whether biological evidence supports an opponent PN difference, a different annotated route, or only an explicitly engineered readout.

An engineered readout must receive recorded/simulated neural activity and documented local feedback only. It must not receive cue-side labels, food coordinates or navigation targets. A fitted decoder needs disjoint training and validation seeds, declared features, frozen coefficients and an explicit architecture decision. Do not subtract the observed left bias to make Gate 3 pass.

### 4. Register the smallest full-network comparison justified by steps 1–3

Choose one mechanism and one supported setting; compare original and candidate, with local-only versus PN-only controls only if required to isolate the mechanism. Freeze exact roots/edges, data/source hashes, parameters, input mapping and decoder. Reserve fresh diagnostic/calibration/held-out seeds. Include no odor, unilateral cues, bilateral cues, repeated pulses and existing recovery windows. Do not launch another Cartesian sweep without a discriminating hypothesis.

Keep the original recovery/burst/support/contrast evidence unchanged. If functional evidence calls for a different readout criterion, write a prospective, versioned scientific protocol change and report both original-gate failures and new results. This is not a bug fix or a retroactive pass.

### 5. Rejoin the end-goal path only after neural checks succeed

Require reproducible responses, recovery, direction/gradient representation, persistent state, unchanged non-learning weights, deterministic continuation and frozen interfaces before embodied tests. Then return to physical direction choice, obstacles/threats, controlled conditioning, held-out learning comparisons, synchronized recordings and actual dashboard delivery acceptance. No learning, consciousness or full biological fidelity claim follows from the present diagnostic.

## Computational and preservation boundaries

The new trace took 32.40 seconds with 1.027 GiB peak process RSS. The two-unit diagnostic plus six native reconstructions took 26.01 seconds with 0.714 GiB peak RSS. These are measured package runtimes, not an ETA for future full-network experiments. Neither package ran the full graph again.

Original experiments, checkpoint payloads and controller source files were preserved. Source hashes were verified after execution. New packages are versioned and refuse to overwrite existing output directories. The 2 GiB free-space reserve remains in force. All source and metadata changes in this phase concern diagnostics, reporting and the requirement ledger.

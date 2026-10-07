# Independent full-network cue diagnostic

Seeds 101–103 are independent of the completed 0–19 evaluation. Each probe starts from rested neural state with matched input RNG and frozen plasticity. Three odor-A/food pairings use the existing experimental rule; post probes retain those weights. No arena controller or parameters were changed.

The two input populations respond distinctly. However, the sets of gamma Kenyon cells that fire at least once during the 200 ms cue windows have Jaccard overlap 0.993–0.996. This binary-set measurement does not establish identical spike timing or firing-rate codes; it does show poor separation for the current presynaptic eligibility rule, which clips activity to a binary indicator.

After pairing odor A, MBON01 drops by 40–47.5 Hz for A and 37.5–40 Hz for unpaired B. Both cues are affected. The selected DNp09 neurons show zero activity for either rested odor-only probe; supplied tonic drive in arena runs is therefore a separate component, and this short assay provides no evidence of odor-driven locomotion through the selected output.

The diagnostic suggests two concrete integration limits: cue-specific eligibility is weak under this encoding, and the selected motor readout does not convey rested odor-only activity. These are limited observations from three short diagnostic states, not proof of a missing anatomical pathway or a biological inability to learn. The original 20-state acquisition/reversal evaluation remains failed.

Evidence: `neural-cue-diagnostic.json`; script `scripts/diagnose_neural_cues.py`; immutable experiment archive with source and hashes under `data/experiments/`. Next investigations must use independent calibration states and prospective acceptance criteria. Any altered thresholds, sensory gains, output populations, or plasticity rule must be versioned before new evaluation.

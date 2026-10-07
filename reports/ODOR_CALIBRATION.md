# Bounded odor encoding calibration

Fifteen full-network cases tested gains 0.05, 0.1, 0.25, 0.5 and 1.0 on independent seeds 201–203. Two rested 200 ms probes per case used matched RNG and frozen weights. No network edges, thresholds, production settings or evaluation criteria were changed.

| Input gain | Mean active gamma-KC fraction | Mean binary-set Jaccard | Mean firing-count cosine |
|---|---|---|---|
| 0.05 | 0.805 | 0.978 | 0.994 |
| 0.10 | 0.813 | 0.994 | 0.998 |
| 0.25 | 0.813 | 0.994 | 0.998 |
| 0.50 | 0.814 | 0.994 | 0.998 |
| 1.00 | 0.814 | 0.995 | 0.998 |

Lower stimulation within this sweep does not produce a clearly separated, sparse gamma-KC representation for the current eligibility mechanism. These are finite-window diagnostics, not a biological sparse-coding benchmark. Very low stimulation, different odor populations, inhibition, thresholds and neuron dynamics were not tested. No setting was promoted.

Evidence is retained in `odor-calibration.json`, `odor-calibration-summary.json` and an immutable source/data archive under `data/experiments/`. The production input gain remains 1.0; the failed acquisition/reversal report remains unchanged. The next investigation should examine where shared activation first develops along the annotated olfactory pathway, before choosing any model alteration.

# Annotated olfactory pathway time-course diagnostic

Six rested full-network traces use independent seeds 301–303 and 20 ms recording bins. Selected populations come from exact pinned annotations: ORN_DM1, ORN_DM2, DM1_lPN, DM2_lPN, APL and gamma Kenyon cells. Every imported network edge remains intact. Frozen plasticity and matched input RNG permit cue comparisons without changing the controller.

In seed 301, the first bin differentiates the projection populations: cue A produces DM1/DM2 means 225/62.5 Hz, cue B 25/150 Hz. In the second bin both projection populations are active for both cues. Broad gamma-KC activity appears at this time and grows thereafter. APL also responds strongly. The full time courses for all three seeds are retained; this example is not a population-wide causal estimate.

The imported outgoing APL connection records are all negative (3,116 and 3,105 records for the two annotated cells), consistent with the table's GABA annotations. No accidental positive-sign substitution was identified in this audit. Signed current-based connections do not establish realistic inhibitory conductances or physiological feedback strength.

These observations suggest that convergence begins before the selected gamma-KC readout. They do not isolate a responsible pathway: recurrent activity, shared projection targets, model dynamics and stimulation remain possible contributors. A causal diagnostic requires a prospectively defined intervention, versioned separately from the unaltered reference brain. Production parameters and the failed acquisition/reversal evaluation remain unchanged.

Evidence: `olfactory-pathway.json`, compact `olfactory-pathway-summary.json`, `apl-sign-audit.json`, and immutable source/data archive under `data/experiments/`.

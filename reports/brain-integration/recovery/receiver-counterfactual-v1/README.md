# Fixed-source receiver diagnostic

Preregistered exploratory comparison using the 28 completed original/local-adaptive direction trials. No new full-brain trial, fitted decoder, learning change, or controller promotion is authorized by this diagnostic.

Predict four recipient units from their recorded incoming events using the existing native Brian2 point-neuron equations. All 28 intact replays must match original spike times/counts exactly and sampled voltage/g/adaptation within 1e-10 mV before any counterfactual. Predict new resets and refractory gates; do not reuse observed gates in the altered-input arms.

The fixed arms retain only DM1 receptor input to the two selected PNs, or remove the three exact paired AOTU019-to-DNa02 records (338 represented anatomical sites). Other recipient units provide unchanged-input controls. All recorded source spike trains stay fixed. A source cannot respond to the intervention, so these comparisons cannot establish a repair in the recurrent full brain.

Use the original PN direction/gradient bounds and separately named descending bounds as descriptive criteria. Keep the original failures, source graph, production controller and acceptance definitions unchanged. Two reused seeds and repeated pulses are diagnostic samples, not independent qualification states.

Run locally with `.venv-next/bin/python scripts/diagnose_receiver_counterfactual.py run` after the protocol commit. The runner verifies frozen source hashes and refuses an existing completed/interrupted output directory. Raw input arrays and replays remain local and are excluded from the public evidence snapshot.

Registration tests: 15 focused partition, event-accounting, recorded-drive and direction-metric tests passed. Execution is complete: 84 native replays, 28/28 intact reconstructions and an independent closed-form audit pass. Both tested input changes leave reliable steering unresolved. Read RESULTS.md, independent-audit.json and ../RECEIVER_DIAGNOSTIC_DECISION.md for evidence and next steps. No new full-brain comparison has been launched.

The native-validation receipt was written after all intact predictions passed and before altered-input replays launched; its `counterfactuals_launched` flag describes that validation-phase timestamp. The final results and progress describe all 84 completed replays.

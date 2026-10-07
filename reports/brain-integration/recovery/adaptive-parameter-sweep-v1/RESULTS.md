# Completed adaptation parameter sweep — no qualifying candidate

All 153 initial trials completed: original plus 18 adaptive settings, two calibration seeds, four cues per arm, and one zero-adaptation regression. None of the 18 settings passed every frozen gate. Held-out and gradient tests were not launched; no controller was promoted.

The grid independently varied 50/150/450 ms decay and 1.5/4.5/13.5 mV spike increments in (a) 685 projection neurons and (b) projection plus explicitly annotated receptor neurons, 2,960 units. Local ALLNs were outside both domains. Learning, signed weights, sensory encoding, motor decoding, and local-inhibition integration remained unchanged.

Counts below separate the combined response/recovery criterion into its components. Response, individual-PN recovery, four-local recovery and signed-DNa02 recovery each have 12 checks per arm; bilateral contrast has four; bursts have 12; walking support has two. This is a reporting breakdown, not a changed criterion.

| Arm | Response | PN recovery | Local recovery | DNa02 recovery | Contrast | Bursts | Support |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t50_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t150_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t450_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t50_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t150_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t450_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t50_b13p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t150_b13p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| projection_t450_b13p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t50_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t150_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t450_b1p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t50_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t150_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t450_b4p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t50_b13p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t150_b13p5 | 12 | 0 | 0 | 0 | 0 | 0 | 2 |
| sensory_projection_t450_b13p5 | 8 | 0 | 0 | 0 | 0 | 0 | 2 |

Stronger and slower-decaying adaptation progressively reduced persistent PN activity. Original individual PN recovery excess was 220–238 Hz; the strongest PN-only setting reduced it to 50–58 Hz. The limit remained 5 Hz. Every setting still failed burst and opponent contrast criteria. At the strongest PN+ORN setting, four unilateral second-pulse response checks fell below 10 Hz, so further suppression also risked removing responsiveness.

These failures do not show that intrinsic adaptation cannot work. They show that this grid in these two domains does not meet the registered requirements. The earlier one-point screen also adapted a wider unqualified local domain and the entire network at 150 ms/1.5 mV; those failed results remain separate evidence.

Evidence: calibration-results.json, gate-breakdown.json, selection.json, zero-regression.json, and the per-trial manifests/continuation receipts. Scheduling amendments document sequential, two-worker and three-worker execution without changing neural conditions. Committed progress snapshots may predate this completion.

The evaluator audited 36,480 ordinary chunks. Including zero regression there are 36,720 complete chunks. All 153 trial manifests report unchanged initial/final effective weight hashes. Thirty-nine fresh-process continuation receipts passed. Individual receipt scope is five continuation windows plus saved whole-network voltage/g/adaptation where applicable; it is not a proof of behavioral fidelity.

Next results: ../adaptive-feedback-trace-v1/RESULTS.md and ../dm1-feedforward-diagnostic-v1/RESULTS.md. These inexpensive diagnostics separate continuing local input from an unsupported opponent readout assumption. Existing failures, protocols and thresholds are retained.

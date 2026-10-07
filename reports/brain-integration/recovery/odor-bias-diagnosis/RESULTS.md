# Completed steps 1–7: odor steering diagnosis

All 40 registered full-network diagnostic trials and their independent raw-event audits completed. A fresh uninstrumented candidate exactly reproduces all 60 windows of the representative instrumented trial: all neuron spike IDs/times/counts, inputs, population rates and commands match.

Preservation, exact annotation/root joins, 60-trial physical field/sensory-clock reconstruction, eight physical turning-sign checks and bounded released-reference artifacts pass. The current production controller remains unchanged.

## Diagnostic measurements

Two fresh diagnostic seeds per condition. Values below are mean left/right DNa02 Hz; raw seed values, selected voltage/g and independently reconstructed signed nominal arrivals remain in diagnostic-results.json. These are descriptive diagnostics, not a new success gate.

| Odor condition | Support Hz | Refractory policy | Pulse L / R Hz | Recovery L / R Hz |
|---|---:|---|---:|---:|
| none | 0 | candidate | 0.0 / 0.0 | 0.0 / 0.0 |
| none | 65 | candidate | 3.0 / 16.0 | 0.7 / 12.1 |
| a_left | 0 | candidate | 51.0 / 0.0 | 50.0 / 0.0 |
| a_right | 0 | candidate | 53.0 / 0.0 | 52.1 / 0.7 |
| a_both | 0 | candidate | 48.0 / 0.0 | 49.3 / 0.0 |
| b_left | 0 | candidate | 52.0 / 0.0 | 58.6 / 2.1 |
| b_right | 0 | candidate | 48.0 / 0.0 | 53.6 / 0.0 |
| b_both | 0 | candidate | 51.0 / 1.0 | 45.7 / 0.7 |
| a_left | 65 | candidate | 51.0 / 0.0 | 51.4 / 2.9 |
| a_right | 65 | candidate | 49.0 / 0.0 | 50.0 / 0.0 |
| a_both | 65 | candidate | 47.0 / 0.0 | 51.4 / 0.0 |
| b_left | 65 | candidate | 50.0 / 2.0 | 42.9 / 0.7 |
| b_right | 65 | candidate | 55.0 / 1.0 | 49.3 / 0.0 |
| b_both | 65 | candidate | 49.0 / 0.0 | 49.3 / 0.0 |
| a_gradient_left | 65 | candidate | 40.0 / 1.0 | 55.7 / 0.0 |
| a_gradient_right | 65 | candidate | 41.0 / 0.0 | 52.9 / 0.0 |
| a_both | 0 | selected_input | 47.0 / 1.0 | 50.7 / 0.7 |
| b_both | 0 | selected_input | 51.0 / 1.0 | 45.7 / 0.7 |
| a_both | 65 | selected_input | 50.0 / 0.0 | 47.9 / 0.0 |
| b_both | 65 | selected_input | 49.0 / 0.0 | 49.3 / 0.0 |

## Interpretation and boundaries

The saved embodied trial preserves a small side-dependent antenna difference, but both placements recruit nearly the same downstream steering state. ORNs stop firing after odor removal while projection and descending activity persist. Physical decoding and exact replay faithfully transmit the bias. The prior held-out directional failure remains unchanged.

Exact annotation hemisphere joins validate the engineered mapping implementation, not physiological antennal receptive-field equivalence. Support-only asymmetry must remain a matched control. Neither support removal, changing odor identity, unilateral stimulation, the mirrored small gradients, nor the selected-input refractory policy resolves the strongly left-biased DNa02 response in these two diagnostic seeds. Support-only stimulation instead produces a modest right-biased readout. Odor-driven activity remains strongly left-biased after odor removal. The refractory comparison changes neural activity but does not repair directional steering. Anatomical cross-hemisphere connections and unequal cell counts do not, by themselves, establish a biological or software defect.

Previously preserved inhibitory interventions implicate model inhibition in right-DNa02 suppression, but their lesions do not establish natural steering or justify deleting inhibition in a production controller. Nominal arrivals in this package are anatomical g increments, not actual membrane currents or fully refractory-gated accepted deliveries.

Reference coverage consists of short native Poisson execution checks, identical-input full-network equation replay and exact source/data/parameter integrity. Published behavioral prediction accuracy, natural receptor responses and long-run stochastic equivalence are not reproduced by those checks.

The registered signed-yaw metric is weaker than source-bearing or actual approach: its ten positive-direction cases must not be described as ten successful food approaches. No navigation, learning or consciousness claim follows.

## Next decision

Step 8 should select a new evidence-supported sensory/state/action hypothesis, with bounded calibration on separate seeds. The present DNa02-difference candidate remains unpromoted. Do not run another large orientation or learning batch until a short frozen candidate distinguishes cue direction and recovers appropriately. Preserve the original full connectome and failed artifacts; do not install a hidden navigator, direct cue-to-turn rule, mirrored artificial wiring or inhibitory lesion as a brain repair.

Trial computation: 1030.2 wall seconds; peak individual worker RSS 2.75 GiB. This excludes startup/auditors and other applications. Performance varied with other active compute.

# Downstream persistence diagnostic

Completed 13 full-network runs, including a delivery-observer parity replay.
Cuts that met the prospective strong-PN-suppression threshold in both seeds:
positive_alln_to_pn_off, all_positive_pn_input_off.

Removing positive ALLN-to-DM1-PN delivery silenced both tested PNs, while left DNa02 activity persisted in both seeds. PN cessation alone does not resolve downstream persistence.

Removing positive output from the two DM1 PNs did not meet the strong PN-suppression threshold; their own output is not required for strong persistent PN activity in these trials.

Removing positive connections within annotated ALLNs did not meet the strong PN-suppression threshold. The tested persistence is not explained by that local-neuron-only connection group alone.

Removing cognate odor-neuron delivery after the pulse did not meet the strong PN-suppression threshold; ongoing odor afferent delivery is not the sole sustaining source.

These are deliberately altered diagnostic networks, not candidate repairs.
model-variants.json distinguishes each temporary transport alteration from the
common base-controller identity in the raw trial manifests.
The application and original controller sources were left unchanged. No learning
or navigation success is claimed. All trials use a left odorA pulse .3-.8s and
constant65Hz supplied walking support. At.8s only selected synaptic transport
weights are zeroed; neural state, topology, other weights and decoder remain fixed.
Pending events encounter the new weight on arrival. Native timing is100μs;
selected membrane-state sampling is1ms.

## Final half-second responses

| Intervention | Seed | DM1 PN mean Hz | ALLN mean Hz | Left DNa02 Hz | Right DNa02 Hz |
| --- | ---: | ---: | ---: | ---: | ---: |
| intact | 11401 | 230.0 | 131.2 | 48.0 | 0.0 |
| intact | 11402 | 225.0 | 131.0 | 50.0 | 2.0 |
| cognate_orn_to_pn_off | 11401 | 225.0 | 131.2 | 54.0 | 0.0 |
| cognate_orn_to_pn_off | 11402 | 225.0 | 131.0 | 50.0 | 2.0 |
| positive_pn_output_off | 11401 | 229.0 | 130.8 | 46.0 | 0.0 |
| positive_pn_output_off | 11402 | 230.0 | 130.9 | 56.0 | 0.0 |
| positive_alln_to_pn_off | 11401 | 0.0 | 130.9 | 44.0 | 0.0 |
| positive_alln_to_pn_off | 11402 | 0.0 | 130.9 | 56.0 | 0.0 |
| positive_alln_recurrence_off | 11401 | 204.0 | 72.4 | 56.0 | 2.0 |
| positive_alln_recurrence_off | 11402 | 205.0 | 72.6 | 60.0 | 0.0 |
| all_positive_pn_input_off | 11401 | 0.0 | 130.9 | 44.0 | 0.0 |
| all_positive_pn_input_off | 11402 | 0.0 | 130.9 | 56.0 | 0.0 |

Strong PN suppression requires at least90% reduction relative to the matched
intact condition in both seeds. DNa02 responses are reported independently:
quieting projection neurons need not quiet a downstream recurrent network.
The ALLN mean spans all429 exactly annotated local neurons; it can hide a small
persistent subpopulation. The detailed artifact also retains actual accepted
positive/negative deliveries and the strongest active input sources into the PNs.

## Verification

All2,080 chunk hashes were checked. Raw spikes matched monitor counts. Inputs
were independently reconstructed from the owned random generator and matched
the intact condition. All intervention trajectories matched intact exactly before
the cut. The additional intact replay with the observer disabled matched spikes,
counts, inputs, commands, selected v/g and refractory gates exactly.

Positive/negative accepted input increments were independently reconstructed
from presynaptic spike ticks, the1.8ms delay, current effective weights and actual
before-synapse refractory gates, including arrivals across chunk boundaries.
All window errors were below1e-6mV. These sums are modeled voltage increments,
not physiological membrane currents or proof of real excitation/inhibition.
The positive/negative signs come from the imported model. ALLN membership comes
from exact-root cell-class annotations, not arbitrary neuron indices.

The frozen protocol identifies every selected edge position against pinned data;
lesion-map.json exports exact source/target roots and synapse counts for all cuts.
The incoming-edge table includes source annotations for the readout neurons.
Effective post-cut weights were hash-checked
against the expected vector and remained fixed afterward. Missing cell labels
are retained as unavailable, not inferred. This two-seed intervention screen
shows dependence on a modeled connection group in the tested state; it does not
identify a unique minimal loop or establish a biological cause.

Trial wall time: 674.3s. Maximum worker RSS:
2.77GiB.
The figure averages two seeds without confidence-interval claims.

Next: use these causal results and accepted-input rankings to choose one bounded
downstream follow-up. Do not promote a lesioned graph, adjust thresholds to force
success, or proceed to learning while sensory recovery/direction remain unpassed.

# Residual-local and steering input diagnostics

Completed fifteen four-second full-network trials. Strong target suppression in
both seeds occurred for: local_plus_alpn_to_alln_off, local_plus_all_external_positive_off, steering_all_positive_off.
No diagnostic variant is promoted; original application sources remain unchanged.

## Final half-second activity

| Condition | Seed | Selected local mean Hz | All local mean Hz | DM1 PN mean Hz | Left steering Hz |
| --- | ---: | ---: | ---: | ---: | ---: |
| local_recurrence_reference | 11501 | 204.0 | 72.9 | 204.0 | 44.0 |
| local_recurrence_reference | 11502 | 204.0 | 72.5 | 204.0 | 50.0 |
| local_plus_alpn_to_alln_off | 11501 | 0.0 | 0.0 | 0.0 | 0.0 |
| local_plus_alpn_to_alln_off | 11502 | 0.0 | 0.0 | 0.0 | 2.0 |
| local_plus_all_external_positive_off | 11501 | 0.0 | 0.0 | 0.0 | 0.0 |
| local_plus_all_external_positive_off | 11502 | 0.0 | 0.0 | 0.0 | 2.0 |
| steering_reference | 11501 | 296.5 | 130.9 | 0.0 | 54.0 |
| steering_reference | 11502 | 294.0 | 130.6 | 0.0 | 50.0 |
| steering_ps013_off | 11501 | 296.0 | 131.0 | 0.0 | 30.0 |
| steering_ps013_off | 11502 | 295.0 | 131.0 | 0.0 | 30.0 |
| steering_top4_off | 11501 | 291.5 | 130.7 | 0.0 | 8.0 |
| steering_top4_off | 11502 | 293.0 | 130.7 | 0.0 | 6.0 |
| steering_all_positive_off | 11501 | 294.0 | 130.4 | 0.0 | 0.0 |
| steering_all_positive_off | 11502 | 293.0 | 130.6 | 0.0 | 0.0 |

Local conditions already cut positive ALLN-to-ALLN recurrence at .8s, then compare
additional ALPN-to-ALLN or all non-ALLN positive inputs. Steering conditions already
silence DM1 PNs by cutting positive ALLN-to-PN input, then compare PS013, four
selected exact sources, or all positive input to left DNa02. All other weights,
neuron state, input events and decoder remain fixed. The two reference conditions
are different diagnostic backgrounds, not intact controls.

## Selection and claims

Four local targets and four steering sources were selected from the pooled prior
published top12 source lists, using11401/11402. This is a bounded candidate pool,
not a claim to a complete pooled all-source ranking. The new seeds11501/11502
are diagnostic probes, not held-out navigation validation. The exact selection
scores, annotations and root IDs were frozen before runs in protocol.json.

Prior local-target input ranking used nominal spike-count-weighted arrivals
because their gates had not been recorded. New data measure actual accepted
inputs into all four targets. results.json distinguishes that accepted source
attribution from the prior nominal hypothesis. ALPN and ALLN membership use
exact cell-class annotations. Missing steering-source cell classes remain
unavailable; exact cell-type labels do not establish function or physiology.

Strong suppression means final target-group mean at most10% of its matched
reference, with reference above10Hz, in both seeds. Individual local-neuron
rates are retained so a mean cannot conceal a surviving member. This screen
shows modeled dependence on an edge set, not a unique minimal biological loop.
The all-positive-input cuts are sanity controls, not proposed brain models.

## Verification

All2,400 chunk hashes were checked. Raw spike events matched monitor counts;
seeded external inputs and fixed motor decoding were independently reconstructed.
Before .8s all variants matched their common pre-intervention state exactly.
The observer-disabled steering-reference replay matched spikes, counts, inputs,
commands, selected v/g and100μs refractory gates exactly.

Accepted positive/negative increments were independently reconstructed with
1.8ms synaptic delay and actual gates, including chunk boundaries; every window
met the1e-6mV tolerance. These are modeled voltage increments, not membrane
currents. Expected whole weight-vector hashes verified that only selected
connections changed. model-variants.json distinguishes each diagnostic graph
from its common base-controller manifest. lesion-map.json retains exact root
IDs and anatomical counts; no reduced controller replaces the full network.

Wall time over all trials: 774.7s. Peak worker RSS:
2.79GiB. No body, reward or learning evaluation ran.
The plot averages two seeds without confidence-interval claims.

Next decisions must distinguish source dependence from physiologically justified
model revision. Keep failures and persistent activity visible; do not promote a
cut graph or infer navigation, learning or consciousness from these diagnostics.

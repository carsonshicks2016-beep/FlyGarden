# Projection-input and local-recurrence factorial diagnostic

Nine four-second full-network runs completed. Strong selected-local suppression against intact in both seeds: joint_off.

| Condition | Seed | Four local mean Hz | ALLN mean Hz | ALPN mean Hz | DM1 PN mean Hz | Left DNa02 Hz |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| intact | 11601 | 295.5 | 131.2 | 84.2 | 227.0 | 52.0 |
| intact | 11602 | 295.5 | 131.0 | 84.2 | 226.0 | 64.0 |
| alpn_to_alln_off | 11601 | 249.0 | 100.9 | 80.2 | 212.0 | 54.0 |
| alpn_to_alln_off | 11602 | 246.5 | 100.7 | 80.2 | 211.0 | 56.0 |
| alln_recurrence_off | 11601 | 202.0 | 72.1 | 73.1 | 202.0 | 44.0 |
| alln_recurrence_off | 11602 | 204.0 | 72.7 | 73.5 | 204.0 | 54.0 |
| joint_off | 11601 | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 |
| joint_off | 11602 | 0.0 | 0.0 | 0.0 | 0.0 | 2.0 |

Positive ALPN-to-ALLN and positive ALLN-to-ALLN transport cuts form a two-by-two comparison. They occur at .8 seconds after the same left odor pulse (.3-.8 seconds). The intact condition retains all weights. Input events, other weights, neural states and fixed decoder are unchanged at intervention. All four selected individual local rates are preserved in results.json. The frozen strong-suppression threshold is at most10% of intact final-half-second selected-local rate, with intact above10Hz, in both seeds. Diagnostic seeds11601/11602 do not establish navigation performance or biological validity.

All1,440 chunk hashes passed. Raw spikes matched counts; inputs and decoding were independently reconstructed. Before .8 seconds trajectories matched exactly. Observer-disabled intact replay matched neural events, inputs, commands and selected v/g/gates exactly. Signed accepted increments were independently reconstructed from delayed spikes and refractory gates across chunk boundaries; all errors were below1e-6mV. Whole-vector hashes verify only specified weights changed. These increments are not biological membrane currents. No learning or body evaluation ran, and no variant is promoted.

Trial wall time: 393.6s. Peak worker RSS: 2.78GiB. The plot averages two seeds without confidence-interval claims. Original application sources remain unchanged.

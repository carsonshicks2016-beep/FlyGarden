# Patchy and il3LN6 sign factorial screen

Thirty-three six-second full-network trials completed. Response/recovery: {'original': False, 'il3_only': False, 'patchy_only': False, 'combined': False}. Sensory contrast: {'original': False, 'il3_only': False, 'patchy_only': False, 'combined': False}. No promotion or application change.

Four model identities isolate original, two-il3LN6 signs only, twelve-patchy signs only and their fourteen-root combination. All138,639 neurons,15,091,983 aggregated records, absolute weights, input encoding, neuron parameters and motor decoder retained. Exact roots and row groups are frozen in protocol.json and model-variants.json. The patchy sign bridge is annotation-supported and qualified in EVIDENCE.md. Nonspiking/graded release, compartmentation and peptide kinetics are not implemented; sign changes are not full biological correction.

Two50Hz odorA pulses occur at .3-.8s and3.3-3.8s under65Hz walking support, for none/left/right/bilateral conditions. Recovery windows are2.5-3.0s and5.5-6.0s. Frozen recovery requires both individual DM1 PNs, each selected local neuron and signed DNa02 within5Hz of same-model/seed support-only. Both pulse responses must increase meanPN at least10Hz; second response uses preceding recovery baseline. Contrast requires opposite left/right PN contrasts relative to none and left-minus-right contrast at least10Hz, in each pulse/seed. Diagnostic seeds11801/11802 are not behavioral validation.

| Model | Cue | Seed | Pulse | Response gain Hz | Max PN recovery difference Hz | Max individual local difference Hz | Signed steering difference Hz | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| original | a_left | 11801 | 1 | 240.0 | 236.0 | 298.0 | 58.0 | fail |
| original | a_left | 11801 | 2 | 17.0 | 232.0 | 298.0 | 46.0 | fail |
| original | a_right | 11801 | 1 | 243.0 | 234.0 | 298.0 | 62.0 | fail |
| original | a_right | 11801 | 2 | 11.0 | 232.0 | 300.0 | 48.0 | fail |
| original | a_both | 11801 | 1 | 250.0 | 230.0 | 300.0 | 54.0 | fail |
| original | a_both | 11801 | 2 | 26.0 | 236.0 | 300.0 | 52.0 | fail |
| original | a_left | 11802 | 1 | 243.0 | 234.0 | 300.0 | 56.0 | fail |
| original | a_left | 11802 | 2 | 21.0 | 232.0 | 300.0 | 68.0 | fail |
| original | a_right | 11802 | 1 | 237.0 | 234.0 | 300.0 | 64.0 | fail |
| original | a_right | 11802 | 2 | 12.0 | 234.0 | 300.0 | 68.0 | fail |
| original | a_both | 11802 | 1 | 254.0 | 230.0 | 298.0 | 64.0 | fail |
| original | a_both | 11802 | 2 | 29.0 | 232.0 | 300.0 | 60.0 | fail |
| il3_only | a_left | 11801 | 1 | 228.0 | 214.0 | 294.0 | 46.0 | fail |
| il3_only | a_left | 11801 | 2 | 21.0 | 220.0 | 296.0 | 34.0 | fail |
| il3_only | a_right | 11801 | 1 | 234.0 | 220.0 | 298.0 | 46.0 | fail |
| il3_only | a_right | 11801 | 2 | 18.0 | 216.0 | 296.0 | 34.0 | fail |
| il3_only | a_both | 11801 | 1 | 240.0 | 216.0 | 294.0 | 42.0 | fail |
| il3_only | a_both | 11801 | 2 | 43.0 | 218.0 | 298.0 | 44.0 | fail |
| il3_only | a_left | 11802 | 1 | 232.0 | 218.0 | 298.0 | 48.0 | fail |
| il3_only | a_left | 11802 | 2 | 25.0 | 222.0 | 296.0 | 50.0 | fail |
| il3_only | a_right | 11802 | 1 | 229.0 | 218.0 | 298.0 | 54.0 | fail |
| il3_only | a_right | 11802 | 2 | 18.0 | 214.0 | 298.0 | 52.0 | fail |
| il3_only | a_both | 11802 | 1 | 246.0 | 210.0 | 298.0 | 36.0 | fail |
| il3_only | a_both | 11802 | 2 | 40.0 | 212.0 | 294.0 | 48.0 | fail |
| patchy_only | a_left | 11801 | 1 | 236.0 | 230.0 | 298.0 | 62.0 | fail |
| patchy_only | a_left | 11801 | 2 | 19.0 | 230.0 | 296.0 | 48.0 | fail |
| patchy_only | a_right | 11801 | 1 | 236.0 | 224.0 | 296.0 | 66.0 | fail |
| patchy_only | a_right | 11801 | 2 | 24.0 | 222.0 | 296.0 | 46.0 | fail |
| patchy_only | a_both | 11801 | 1 | 253.0 | 224.0 | 296.0 | 58.0 | fail |
| patchy_only | a_both | 11801 | 2 | 37.0 | 236.0 | 296.0 | 56.0 | fail |
| patchy_only | a_left | 11802 | 1 | 237.0 | 224.0 | 298.0 | 52.0 | fail |
| patchy_only | a_left | 11802 | 2 | 20.0 | 224.0 | 298.0 | 66.0 | fail |
| patchy_only | a_right | 11802 | 1 | 239.0 | 228.0 | 298.0 | 58.0 | fail |
| patchy_only | a_right | 11802 | 2 | 19.0 | 224.0 | 296.0 | 68.0 | fail |
| patchy_only | a_both | 11802 | 1 | 252.0 | 226.0 | 296.0 | 58.0 | fail |
| patchy_only | a_both | 11802 | 2 | 33.0 | 222.0 | 296.0 | 70.0 | fail |
| combined | a_left | 11801 | 1 | 226.0 | 208.0 | 294.0 | 46.0 | fail |
| combined | a_left | 11801 | 2 | 24.0 | 210.0 | 294.0 | 30.0 | fail |
| combined | a_right | 11801 | 1 | 226.0 | 212.0 | 294.0 | 44.0 | fail |
| combined | a_right | 11801 | 2 | 14.0 | 210.0 | 288.0 | 32.0 | fail |
| combined | a_both | 11801 | 1 | 241.0 | 212.0 | 292.0 | 48.0 | fail |
| combined | a_both | 11801 | 2 | 36.0 | 218.0 | 292.0 | 38.0 | fail |
| combined | a_left | 11802 | 1 | 228.0 | 208.0 | 294.0 | 58.0 | fail |
| combined | a_left | 11802 | 2 | 23.0 | 210.0 | 294.0 | 48.0 | fail |
| combined | a_right | 11802 | 1 | 224.0 | 214.0 | 296.0 | 52.0 | fail |
| combined | a_right | 11802 | 2 | 18.0 | 210.0 | 292.0 | 54.0 | fail |
| combined | a_both | 11802 | 1 | 243.0 | 206.0 | 296.0 | 44.0 | fail |
| combined | a_both | 11802 | 2 | 40.0 | 208.0 | 292.0 | 50.0 | fail |

All7,920 chunks passed hashes and spike/count parity. Input RNG and exact clock ticks independently reconstructed; paired events and fixed decoding match. Actual delayed/gated positive and negative increments independently reconstructed across chunk boundaries within1e-6mV. These are voltage increments, not membrane currents. Every model checkpoint continued five windows in a fresh process with exact neural/input events and motor, and whole v/g<=1e-10mV. Combined observer-disabled parity matched exactly. All source/weight hashes passed.

Trial wall time 1655.3s; peak workerRSS2.58GiB. One worker; plot two-seed ranges are not confidence intervals. No body, navigation or learning acceptance. Preserve failed criteria without sign tuning or blanket inhibitory conversion.

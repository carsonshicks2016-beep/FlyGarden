# Two-il3LN6 sign candidate: response and recovery

Seventeen six-second full-network trials completed. Candidate response/recovery prerequisite: **failed**. Candidate sensory contrast prerequisite: **failed**. No controller promotion or application change.

Exactly3,546 outgoing weights of roots720575940623636701 and720575940632403986 are multiplied by−1 before simulation. All138,639 neurons,15,091,983 aggregated connection records and absolute weight magnitudes are retained. No peptide dynamics, compartments, adaptation, other signs, neuron parameters, sensory encoding or decoder are changed. Learning is disabled. The sign change is a source-supported cell-type hypothesis, not validated biology.

Trials use support-only, left, right and bilateral synthetic odorA. The same condition is presented at .3–.8s and3.3–3.8s. Recovery windows are2.5–3.0s and5.5–6.0s. A response must increase mean DM1 PN firing by at least10Hz; for the second pulse the reference is the first recovery mean. Recovery requires both individual PNs and all four selected local neurons within5Hz of same-model/same-seed support-only, plus signed DNa02 within5Hz. These frozen gates apply to every non-none cue, both pulses and both diagnostic seeds.

| Model | Cue | Seed | Pulse | Response gain Hz | Max PN recovery difference Hz | Max individual local difference Hz | Signed steering difference Hz | Gate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| original | a_left | 11701 | 1 | 241.0 | 232.0 | 298.0 | 54.0 | fail |
| original | a_left | 11701 | 2 | 15.0 | 230.0 | 300.0 | 52.0 | fail |
| original | a_right | 11701 | 1 | 243.0 | 238.0 | 302.0 | 56.0 | fail |
| original | a_right | 11701 | 2 | 14.0 | 230.0 | 300.0 | 48.0 | fail |
| original | a_both | 11701 | 1 | 253.0 | 232.0 | 302.0 | 52.0 | fail |
| original | a_both | 11701 | 2 | 27.0 | 234.0 | 300.0 | 48.0 | fail |
| original | a_left | 11702 | 1 | 241.0 | 234.0 | 298.0 | 76.0 | fail |
| original | a_left | 11702 | 2 | 15.0 | 228.0 | 302.0 | 58.0 | fail |
| original | a_right | 11702 | 1 | 242.0 | 230.0 | 298.0 | 78.0 | fail |
| original | a_right | 11702 | 2 | 21.0 | 230.0 | 300.0 | 56.0 | fail |
| original | a_both | 11702 | 1 | 253.0 | 230.0 | 300.0 | 76.0 | fail |
| original | a_both | 11702 | 2 | 28.0 | 236.0 | 300.0 | 46.0 | fail |
| sign_only | a_left | 11701 | 1 | 231.0 | 224.0 | 296.0 | 34.0 | fail |
| sign_only | a_left | 11701 | 2 | 21.0 | 214.0 | 298.0 | 40.0 | fail |
| sign_only | a_right | 11701 | 1 | 230.0 | 212.0 | 294.0 | 52.0 | fail |
| sign_only | a_right | 11701 | 2 | 25.0 | 220.0 | 296.0 | 40.0 | fail |
| sign_only | a_both | 11701 | 1 | 248.0 | 214.0 | 296.0 | 40.0 | fail |
| sign_only | a_both | 11701 | 2 | 39.0 | 222.0 | 296.0 | 48.0 | fail |
| sign_only | a_left | 11702 | 1 | 230.0 | 218.0 | 294.0 | 56.0 | fail |
| sign_only | a_left | 11702 | 2 | 24.0 | 216.0 | 296.0 | 54.0 | fail |
| sign_only | a_right | 11702 | 1 | 232.0 | 216.0 | 296.0 | 40.0 | fail |
| sign_only | a_right | 11702 | 2 | 18.0 | 216.0 | 296.0 | 34.0 | fail |
| sign_only | a_both | 11702 | 1 | 250.0 | 216.0 | 296.0 | 64.0 | fail |
| sign_only | a_both | 11702 | 2 | 33.0 | 218.0 | 298.0 | 36.0 | fail |

Sensory contrast separately requires the left PN contrast to exceed the right contrast by10Hz and opposite signs relative to support-only in each seed/pulse. It does not validate physical movement direction or navigation.

## Verification and resources

All4,080 chunk hashes and raw spike/count identities passed. Owned input RNG events and exact integer ticks were reconstructed; decimal timestamps agreed within1e-12s. Paired input events and fixed decoding matched exactly. Positive/negative accepted voltage increments reconstructed from1.8ms-delayed spikes and100µs gates passed the1e-6mV tolerance across chunk boundaries; these increments are not biological currents. Whole weight hashes establish that only the selected signs changed and remained fixed.

The observer-disabled candidate replay matched all spikes, inputs, commands and selected state/gates exactly. Original and candidate checkpoints continued for five windows in fresh processes with exact events/counts/inputs/motor and whole-network v/g differences at most1e-10mV. Checkpoint receipts report selected-source spikes in the pending delay horizon; they do not invent pending events when none occurred.

Trial wall time: 919.7s. Peak worker memory: 2.66GiB. One worker. Two diagnostic seeds provide a bounded screen, not population statistics. No body, reward or learning evaluation ran.

The original v1 one-chunk interruption is preserved. AMENDMENT.json documents the recording-only timestamp-check correction; no scientific criterion, seed or model parameter changed. The anatomical sign candidate retains versionv1; recording protocol isv2.

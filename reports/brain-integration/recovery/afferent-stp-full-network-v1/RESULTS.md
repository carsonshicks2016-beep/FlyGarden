# Full-network afferent STP-only comparison

Completed 12 four-second full-network trials and fresh-process checkpoint
continuation for both model identities. The recovery prerequisite for STP-only
failed. No controller was promoted and the application remains unchanged.

The engineered variant gives independent release-resource state to 351 exact
cognate DM1/DM2 ORN-to-lPN aggregated records, using generic published U=.24,
tauD=.1s and tauF=.05s. The rested first delivery is normalized to the original
voltage weight. Presynaptic inhibition is absent. This normalization, aggregated
per-edge state and parameter application are engineered assumptions, not validated
DM1/DM2 physiology. All 138,639 neurons and 15,091,983 effective graph records
remain represented; 351 original storage weights are zero and their matching
stateful synapses provide the effective delivery. Nonselected weights and decoder
remain fixed; learning is disabled.

## Prospective recovery screen

Compare each cue with same-model/same-seed support-only control. Recovery requires
both tail differences within 5Hz and a pulse PN increase of at least10Hz in every
STP-only case. This two-seed screen is a prerequisite, not statistical validation.
The PN measure is the mean over the two mapped DM1 lPNs.

| Model | Seed | Cue | Pulse PN increase Hz | Final PN difference Hz | Final signed DNa difference Hz | Gate |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| original | 11301 | a_left | 238.0 | 226.0 | 60.0 | fail |
| original | 11301 | a_right | 244.0 | 228.0 | 60.0 | fail |
| original | 11302 | a_left | 240.0 | 229.0 | 64.0 | fail |
| original | 11302 | a_right | 240.0 | 222.0 | 58.0 | fail |
| stp_only | 11301 | a_left | 238.0 | 230.0 | 58.0 | fail |
| stp_only | 11301 | a_right | 235.0 | 227.0 | 60.0 | fail |
| stp_only | 11302 | a_left | 237.0 | 223.0 | 56.0 | fail |
| stp_only | 11302 | a_right | 236.0 | 225.0 | 52.0 | fail |

## Verification and limits

All1,920 chunk hashes, raw spike-count matches, population rates, input RNG
reconstructions and fixed decoder reconstructions passed. Both variants received
exactly identical external events for each matched cue/seed. Stored base weights
did not change during trials; only the STP release multiplier changed.
The two support-only recordings have identical spikes and counts in all160
windows. Pulse recordings differ substantially across the full network, so the
mechanism was active; that changed activity did not meet the recovery prerequisite.

Each checkpoint was saved during stimulation at .775s, then reopened in a new
process. The next five windows matched spikes, counts, inputs and motor output
exactly; whole-network v/g and STP x/u/last-update differences met the registered
tolerances. The receipt reports how many selected presynaptic spikes occurred in
the pending-delay horizon, rather than assuming every checkpoint tests that path.
The separate native micro-test explicitly verifies restoration with a queued delivery.
Brian2 stores event-driven x/u lazily together with their last-update times;
recovery between events is evaluated analytically on the next event. Stored x/u
values alone should not be read as current-time physiological measurements.

Trial wall time: 585.0s; maximum worker RSS:
2.77GiB; package storage before this report:
0.54GiB. Initialization/checkpoint costs are included;
fresh-process continuation-worker times are not included in trial wall time.

Next: retain this failed afferent-only result and preregister targeted downstream persistence diagnostics. Do not expand STP to arbitrary connections or proceed to navigation/learning.
No inference about consciousness, behavioral learning or autonomous navigation follows.

[Published source](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2021.730431/full)
and prior isolated event/reference packages establish the mechanism basis, not
biological parameter validity for this application.

# Continuous candidate operating-state calibration

Six full-network/body trials completed. Independent reconstruction verifies owned-RNG inputs,spike counts,population rates,fixed decoder commands,causal25ms holds,and90 physical poses per3-second trial.

| Seed | Support Hz | Departure mm | Heading rad | Flips |
|---|---|---|---|---|
| 9501 | 0 | 0.075 | 0.002 | 0 |
| 9502 | 0 | 0.046 | -0.001 | 0 |
| 9501 | 30 | 7.567 | -0.193 | 0 |
| 9502 | 30 | 9.681 | -0.261 | 0 |
| 9501 | 65 | 18.795 | -0.312 | 0 |
| 9502 | 65 | 21.217 | -0.406 | 0 |

The prospective rule selects65Hz: both seeds depart more than10mm with finite observations and no flipped samples.30Hz does not pass this criterion. This freezes operating support,not sensory choice.

Fresh-process continuation from1.5s reproduces spikes,inputs,counts,commands,body observations,andposes through3s exactly. Original per-window full neural/physical hidden-state arrays were not recorded; stronger state comparison remains pending. Initial pose for metric auditing was independently reconstructed from the pinned body constructor because original calibration manifests omitted it.

No held-out seeds were used. Neural weights and decoder remain fixed. Navigation,escape,andbehavioral learning are unvalidated.

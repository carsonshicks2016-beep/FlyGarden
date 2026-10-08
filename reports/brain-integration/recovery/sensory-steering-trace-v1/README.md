# Saved sensory-to-steering analysis

This package analyzes the completed 28-trial local-adaptation-direction-v1 archive. It creates no neural simulations, modifies no controller and introduces no qualification criterion. The archive already has known directional failures; freezing this analysis does not make these data held out.

`protocol.json` pins the analysis before execution. `population-roots.json` joins exact annotation labels to model indices and root IDs. Selection follows the olfactory pathway and the candidate steering routes in Rayshubskiy et al., Figure 7, plus fixed olfactory, mushroom-body, lateral-horn and central-complex classes. LAL171 and LAL074 have no exact type matches in these annotations; they remain unavailable.

The 18 input-attribution targets comprise the two DM1 PNs, two DNa02 cells, two APLs, two MBON32s, two LAL170s, two DNa03s, two LAL018s and the four previously monitored local cells. Eight targets have saved state samples that independently check reconstructed g/adaptation. Ten have spike-derived g reconstructions without independent state observations. No membrane voltage is reconstructed. All reported state extrema are over 25 ms endpoint samples, not continuous extrema.

Analysis phases use half-open simulated-time intervals: pre, first 100 ms of each pulse, remaining 400 ms, complete 500 ms pulse, first 300 ms after offset, and the original final 500 ms recovery windows. Synaptic phases use delayed arrival time. Accepted delivery respects each target's recorded spike/reset/refractory gates. Positive and negative voltage-equivalent increments remain separate; their units are mV/s, not measured biological currents. This is descriptive accounting, not a causal intervention.

With local archives present:

```sh
.venv-next/bin/python scripts/trace_sensory_steering.py analyze
```

The analyzer refuses to overwrite completed results. `results.json` contains bounded phase summaries, individual named-route rates, signed input sources and reconstruction checks. Local `profiles/*.npz` preserve 25 ms rates, counts, exposure, commands and sampled/reconstructed states. Raw prior trials, checkpoints and derived profiles remain local and excluded from GitHub. The public snapshot alone cannot independently reproduce the raw-event audit.

Rates, population differences and equal-reference subtraction are descriptive. No readout is fitted, no new score substitutes for the failed original gates, and no controller is promoted. Soma-side labels alone do not establish sensory receptive-field side.

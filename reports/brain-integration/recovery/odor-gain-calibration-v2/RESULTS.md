# Steps 8–11: lower-gain calibration result

24 registered full-network trials completed; raw spike/input/clock/count/decoder/probe audits passed. Fixed full network, support and decoder; no learning or application controller change.

| Gain Hz | Seed | Left change Hz | Right change Hz | Bilateral change Hz | Recovery gate | Overall |
|---:|---:|---:|---:|---:|---|---|
| 1 | 9901 | 50.0 | 0.0 | 56.0 | False | False |
| 1 | 9902 | 12.0 | 52.0 | 56.0 | False | False |
| 5 | 9901 | 54.0 | 40.0 | 58.0 | False | False |
| 5 | 9902 | 56.0 | 66.0 | 58.0 | False | False |
| 10 | 9901 | 52.0 | 60.0 | 56.0 | False | False |
| 10 | 9902 | 62.0 | 64.0 | 66.0 | False | False |

Values are signed DNa02 left-minus-right rates relative to matched no-odor controls. Baseline subtraction is evaluation only; the controller remains unchanged. This two-seed engineered capability screen is not held-out navigation evidence. All four gates must pass in both seeds.

No tested gain passes. Step 10 calibration failed; no candidate is frozen/promoted. Step 11 held-out navigation is not started because its prerequisite failed. Missing activity is not successful direction, and the prior held-out failure remains intact.

Next: investigate the model’s odor-to-steering pathway and operating-state assumptions using an independently supported mapping or physiology revision. Do not fit cue-to-turn weights, remove inhibition or relabel a supplied navigator as neural control. The amplitude-only hypothesis is exhausted within this registered grid.

A fresh uninstrumented full-network replay of the 1 Hz bilateral trial matches all 60 recorded windows exactly: individual spike IDs/times/counts, external inputs, population rates and motor commands. This establishes bounded recording parity, not navigation.

Trial computation totaled 349.3 wall seconds, excluding other setup/audits; peak trial-worker memory was 2.45 GiB. Retained calibration artifacts occupied about 55 MiB before final report metadata.

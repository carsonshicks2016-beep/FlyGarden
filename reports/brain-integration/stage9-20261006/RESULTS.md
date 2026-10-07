# Step 9 — behavioral progression entry

Status: **blocked_by_measured_response**. The complete Step 8 evidence was independently audited before this decision. No navigation, predator or foraging trials were launched and the live controller remains unchanged.

| Required Step 8 gate | Result |
|---|---|
| causal motor effect | PASS |
| directional avoidance | FAIL |
| useful response | FAIL |
| exact motor replay | PASS |

Measured useful-response counts: 0/20 gain at least 0.05 radians away heading; 0/20 depart at least 0.1 mm from their matched input-off body; 20/20 avoid flips. The required counts remain 16, 16 and 18, respectively.

Across the intact trials, the selected DNp09 forward-drive cells emitted **0 spikes**, and the two DNa02 steering cells emitted **98 spikes**. The tested decoder's forward-rate term therefore remains zero; small steering-derived commands still reach the body. This is a measured limitation of the current stimulus/network/readout combination, not evidence that the spike recorder or complete brain is inactive. Maximum physical departure from the matched input-off body was **0.029292 mm**.

## Next dependent work

If an entry gate fails, first diagnose the sensory-to-descending response and its conversion to actual body motion. Keep existing failure records and thresholds. Any revised sensory encoding or decoder becomes a new, versioned candidate, calibrated on separate seeds and then tested on held-out matched trials. Adding a walking drive or escape controller is an explicit engineered intervention and must never be hidden behind the brain label.

After entry readiness, the progression is: live local cue response → orientation → obstacle navigation → unfamiliar layouts → approaching threats → food collection under danger. Each level needs fresh body-generated sensory observations, matched sensory-off controls, recorded collisions, falls and stalls, and a committed evaluation protocol before trials. The Step 8 stationary-camera recordings do not substitute for this live feedback. A failed level stops progression to the next; game unlocks do not certify scientific success.

The full measured evidence and motor-population diagnosis are in [Step 8](../stage8-20261006/RESULTS.md). `readiness.json` pins that audited result by hash. Rerun this check with `.venv-next/bin/python scripts/check_behavioral_readiness.py`.

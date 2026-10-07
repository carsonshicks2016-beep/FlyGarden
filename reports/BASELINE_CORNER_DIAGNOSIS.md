# Baseline corner failure: seed 602

The recorded trial collected three food rewards, then fell at 55.9 seconds. From 52.6 seconds onward the thorax remained near the northwest boundary (approximately x=-39 mm, y=29 mm), while all three local obstacle rays repeatedly measured 0.25 mm. Commands remained a strong differential forward drive. Thorax height rose as high as 2.35 mm in the last retained pre-fall sample, then dropped to 0.63 mm with the flipped flag.

These observations distinguish the failure from an unobserved open-ground instability. They are consistent with continued forward drive in a confined corner. The recording does not retain full raw MuJoCo contact lists, so exact contact impulses and a causal explanation are not established.

Do not change the ongoing ten-trial evaluation: it measures the fixed v3 controller. A separately versioned recovery candidate should respond to locally trapped observations, retain all physical contacts, and use no world coordinates or teleportation. FlyGym's pinned HybridTurningController supports signed descending inputs by reversing CPG frequencies; Fly Garden currently clips body commands to nonnegative drive. Backward recovery therefore requires explicit body-adapter validation before promotion. It must remain a supplied baseline behavior, not a full-brain or learning claim.

Suggested independent test: initialization near each corner; matched baseline v3 versus recovery candidate; evaluate actual exit from the confined region, food contact, falls, stalls and path. Freeze the candidate before held-out arena trials. Any changes to allowed motor bounds and checkpoint/controller versions must be documented.

Evidence: baseline-acceptance.json; recording 5810568da1864165ae9376a9eaae70c1; outcome.json and recording SHA retained in that folder; pinned FlyGym turning_controller.py.

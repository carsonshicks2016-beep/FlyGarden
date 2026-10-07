# Physical obstacle exposure diagnosis

The independent diagnostic uses seeds 101 and 102, fixed straight drive `[1,1]`, and ten simulated seconds per geometry. It records raw MuJoCo obstacle contacts, body positions, and flips. It changes neither physics parameters nor controller weights. See `obstacle-diagnostic.json` and `scripts/diagnose_obstacles.py`.

Both 0.15 mm step trials crossed the step without flipping. A 3 mm wall is taller than the body and the fixed command continues driving into it; the first wall trial flips after contact. This distinguishes shallow traversal from a hard-wall collision. It does not prove stable obstacle navigation, a valid escape reflex, or arbitrary uneven-terrain walking.

The integration appends obstacle geometries to FlyGym's ground geometry list before adding the fly. FlyGym generates explicit contact pairs, and its supplied controller queries ground-only body-segment contact forces. The diagnostic confirms actual obstacle contacts. There is no evidence here for repairing collisions by disabling them, teleporting the body, or inserting a hidden route planner.

Next: validate an explicitly labeled egocentric avoidance interface against fixed sensory-only probes, identically for frozen and learning-enabled conditions; maintain the full-brain model's distinction from the supplied baseline. General shallow terrain requires a longer multi-layout test before a broader stability claim.

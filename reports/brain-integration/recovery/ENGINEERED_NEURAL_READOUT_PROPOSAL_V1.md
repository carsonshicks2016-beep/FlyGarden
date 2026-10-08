# Contingent architecture proposal: engineered neural readout, version1

Prepared2026-10-07 from the completed sensory/route diagnostics. The completed fixed sensory-context comparison fails full original direction0/4 in each context, so its registered stopping rule selects this architecture branch next. This is a proposal; no fitted readout, changed production controller or new training run is delivered by this document.

## Purpose and honest scope

Try to turn measured neural side information into useful bounded steering without pretending that the tested native descending pathway already works. The full modeled graph still advances continuously and produces the features. A fitted readout is additional engineering. It bypasses part of the mushroom-body/intermediate/descending circuit and must be visible in the controller identity, viewer, recordings and experiment reports.

This branch can test neural activity -> movement. It does not repair the biological fidelity of138,639 point neurons or prove that the whole network performs the animal's native computation. It must not quietly replace the network with a route planner.

## Smallest primary candidate

Start with the two exact DM1 projection neurons already monitored and independently reconstructed:

| Feature | Exact root ID | Modeled index |
|---|---|---:|
| DM1_lPN left | 720575940630770042 | 100454 |
| DM1_lPN right | 720575940619071005 | 37714 |

Use their causal recent spike rates, with a preregistered finite rate window or fixed filter, to form a small constrained linear signed readout. Specify the coefficients, calibration loss, numerical bounds, rate window/filter and neutral behavior before fitting. Keep the first candidate to these two features; do not search thousands of neurons against held-out results. Their unequal effective input scale motivates calibration, but does not justify changing anatomical weights or claiming a physiological correction.

Keep existing DNp09-based forward drive and supplied leg coordination explicit. The new signed readout supplies a bounded turn command through a versioned motor adapter. The adapter receives neural features only. It receives no food/predator coordinates, cue-side labels, arena map or target route at runtime. Calibration fixtures can have labeled stimuli; those labels may be used by the offline fitting procedure, never passed into the running controller. Record that distinction.

A direct ORN contrast can be retained as a separately labeled sensory positive control. It would bypass more of the network than the PN candidate and cannot serve as evidence that the deeper brain circuit works. It is not an automatic fallback controller hidden behind the connectome label.

## Calibration and prospective tests

1. Use existing local-adaptive recordings on seeds12301/12302 only for exploratory calibration. They have known failures and informed this architecture choice; they are not independent validation evidence. Verify raw spike/hash/clock integrity before fitting.
2. Register the final model class, fitting rule, exact features, bounds and source/data hashes. Fit only that rule on calibration data, save coefficients and hash the complete controller. Inspect saturation and neutral behavior without tuning against future tests.
3. Run a small fresh diagnostic screen before the costly qualification batch. Declare its seeds/cases and decision rule before computation. A passed screen supports proceeding; it is not navigation competence.
4. Freeze disjoint held-out seeds before launching at least20 matched independent states per condition for formal sensory acceptance. Include no odor, unilateral sides, full bilateral,50/50,60/40,40/60, sensory-off and shuffled/appropriate control conditions. Use balanced schedules and unrewarded probes where relevant.
5. Preserve original unfitted PN and DNa02 metrics alongside separately named adapter metrics. The original neural Gate3/6 failures remain failures. Prospectively state the adapter's directional/gradient separation, neutral/recovery, timing and motor bounds; do not silently reuse a transformed score as a historical pass.
6. If this fixed readout fails fresh gradient/direction acceptance, diagnose feature information and noise before adding complexity. No held-out coefficient adjustment or expanding feature search against those same seeds.

## Rejoining the arena

After neural acceptance, verify physical turn signs, stopping/forward behavior, persistent brain state and common simulation time using actual body observations. Then test open-ground food acquisition, local odor gradients, obstacle layouts and shelters on unfamiliar seeded arenas. Record falls, stalls, collisions and capture; compare frozen readout/control identities. Supplied gait and escape behaviors remain visible and identical across any later learning comparisons.

Every run retains raw neural/body events, immutable checkpoints and source/controller hashes. Pause/restore, complete-scene continuation, lineage branching and recorded playback must be tested with the new adapter's filter/decoder state included in checkpoints. Simulate at natural speed and use recorded viewing when below real time; never skip neural dynamics to produce smoother gameplay.

## Learning requires its own causal path

A PN-only navigation adapter does not establish that KC-to-MBON plasticity can change behavior. Before odor-choice learning, identify exact annotated reinforcement compartments and a documented update direction, then demonstrate that the readout receives information downstream of the selected plastic connections. If it does not, redesign that learning interface openly rather than declaring PN steering a mushroom-body learning success.

Keep neural weight adaptation, readout calibration and reinforcement learning distinct. Test controlled acquisition, saved-state retention, reversal and generalization against learning-disabled and shuffled-pairing controls, with the original20-state/bootstrap requirements. No PPO, GA or game-score substitution is needed to prove the first learning mechanism.

## Decision boundary

The fixed context trial decides whether to continue the tested native MBON32/DNa02 branch. Failure selects this proposal for detailed registration; it does not validate the proposal. Successful engineered steering would narrow the application bottleneck, while native-route fidelity, vision, embodied robustness and learning remain separately unproven. Larger navigation or learning architecture changes require an explicit recorded scope decision and honest labels.

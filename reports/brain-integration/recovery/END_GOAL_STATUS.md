# What remains to make Fly Garden work as intended

Status snapshot2026-10-07. This file distinguishes a running modeled network, useful neural control and a completed learning application. It is not a percentage-complete estimate.

## Established in the checked scope

- The available full point-neuron graph runs:138,639 modeled neurons,15,091,983 aggregated connection records and54,492,922 represented anatomical sites.
- Exact-ID sensory stimulation produces recorded neural responses. Selected input/output/state reconstructions, checkpoint continuations and interrupted-recording recovery pass numerical checks.
- The395-cell local-adaptation candidate resolves the tested odor persistence problem:28 original/candidate trials retain successful candidate response, recovery and repeat response across the tested cues. This is an engineering cooldown, not a physiological fit to each root.
- Direct MBON32 activity reaches the selected DNa02 steering neurons through imported inhibitory connections. The saved-run audit distinguishes actual delivery, refractory rejection, competing signed input and count/timing effects.
- The project has arena, supplied locomotion, recording/playback, brain-viewer and export infrastructure. That infrastructure does not establish useful sensory navigation or learning.

## The remaining dependencies

| Requirement | Current practical meaning |
|---|---|
| Reliable sensory-dependent direction | The tested raw PN and DNa02 readouts fail opposed direction and reliable unequal-gradient acceptance. The completed16-trial matched context comparison also fails full direction0/4 in both contexts, although odor makes the right input rate-sensitive. See `sensory-context-capability-v1/RESULTS.md`. |
| Explicit action architecture | If the fixed native route fails, register an engineered neural readout openly. Keep the full graph advancing, use neural/local observations only and preserve the old failed criteria. Fit and held-out validation must remain separate. |
| Physical neural control | A qualified readout must turn the real simulated body in the correct direction, persist across neural windows and respond to actual local fields. Validate stopping, food contact, obstacles, stalls/falls and unfamiliar layouts. A neural-only pulse test cannot establish any of these. |
| Vision and threat inputs | Earlier vision encoder failures remain unresolved in the acceptance ledger. Validate actual eye images, own-body masking, occlusion, looming features and annotated neural mappings before claiming scenery-dependent visual behavior. |
| Controlled learning | Demonstrate that selected plastic connections actually affect the behavior/readout. Test acquisition, retention, reversal and generalization with learning-disabled/shuffled controls and the required independent states and bootstrap interval. No current candidate has this qualification. |
| Complete application workflow | Exercise the real browser and launcher, scene editing, immutable learned/full saves, branching, playback/free cameras and durable export jobs together with the chosen controller. Retain unsuccessful trials and display controller/model coverage honestly. |

The immediate bottleneck is functional sensory-to-action conversion. Resolving it would unblock embodied experiments; it would not finish vision, learning or end-to-end delivery. There is no defensible completion percentage or completion date while those scientific gates remain open.

## Useful stopping point for the current diagnosis

The matched sensory context did not restore full original direction. Stop widening the MBON32/DNa02 stimulation/adaptation grid. The next branch is the explicitly proposed engineered readout in `ENGINEERED_NEURAL_READOUT_PROPOSAL_V1.md`, with separate calibration and prospective checks. That is a documented architecture change, not proof that the original biological route has been repaired.

All39 requirement texts and qualification statuses in `../acceptance-ledger.json` remain authoritative. Bounded success establishes the named check, not the entire brain or project. A failed direction check does not prove the full graph has no useful information. A fitted adapter, weight change, attractive video or active brain overlay does not establish learning or biological fidelity.

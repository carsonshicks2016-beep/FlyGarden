# Fly Garden: start here for an independent review

Fly Garden is Carson Hicks's local research and visualization project, developed with substantial AI assistance from OpenAI Codex. Carson supplied the goals, project direction and review decisions; Codex wrote and revised much of the implementation, designed diagnostics and operated experiments under Carson's authorization. The connectome data, upstream neural model, physics engine and body model were produced by their credited researchers. This is not a claim that Carson independently discovered or reconstructed a fly brain.

## What it does

The application puts a modeled fly in a small 3D arena. A Python service advances a neural simulation and a physical body; a browser displays the arena and recorded neural activity. Odor is sampled locally, neural spikes are translated into movement commands, and a supplied walking controller coordinates the legs. Food, obstacles and a ground predator provide experimental situations.

The neural graph represents 138,639 neurons, 15,091,983 aggregated connection records and 54,492,922 represented anatomical synapses from FlyWire version 783. An anatomical connection is not a full biophysical description: each modeled neuron is a simplified electrical unit. A saved state preserves model variables, not a claim of consciousness or an animal's identity.

## How it is made

1. Import upstream graph data and exact neuron IDs, preserving provenance and hashes.
2. Use Brian2 to simulate electrical units and synaptic events on a shared clock.
3. Encode engineered sensory signals into annotated input populations.
4. Decode selected descending-neuron activity into bounded forward and turning commands.
5. Use FlyGym/NeuroMechFly and MuJoCo for body mechanics and supplied leg coordination.
6. Stream sampled state to a Three.js interface; record spikes and poses in compressed chunks.
7. Preserve full checkpoints for continuation and recordings for inspection, playback and video export.
8. Test claims using fixed seeds, matched controls, frozen protocols and retained failures.

Creating the application mostly involves writing adapters and infrastructure around existing scientific tools, then checking whether the assumptions produce useful behavior. Connecting a graph to a body does not automatically make it a functioning biological brain.

## Current scientific problem

In the baseline model, an odor pulse starts activity in the modeled smell circuit that persists after the pulse ends. Persistent activity makes subsequent cues and left/right differences difficult to use. This is a simulation failure, not a diagnosis of epilepsy in a real fly.

The previous fixed-point adaptive-LIF screen completed 21 full-network trials. All 5,040 chunks passed integrity checks; disabling adaptation exactly reproduced baseline events and voltage/conductance states. Adaptation lowered firing but failed recovery and directional contrast at the tested setting. No candidate was promoted.

The completed sweep tested a temporary firing cooldown: each spike adds a voltage-equivalent adaptation term that decays over time. The fixed grid used 50/150/450 ms decay and 1.5/4.5/13.5 mV increments, separately in projection neurons and in projection plus annotated olfactory receptor neurons. All 153 initial trials finished; none of the 18 adaptive settings passed every calibration gate. Held-out and unequal-intensity tests were therefore not launched. These parameters are engineering hypotheses, not fitted calcium/potassium channels.

Follow-up attribution traced 24 existing recordings and reconstructed selected neural states. Under the strongest settings, local neurons supply over 99% of accepted positive input into the two monitored projection neurons after odor removal. A separate two-neuron replay removed recurrent input: recovery became quiet, but both unilateral cues still produced a positive left-minus-right readout. Persistence and the unestablished opponent readout are separate problems. No production controller changed. See POST_SWEEP_DECISION.md for limitations and the next discriminating checks.

A new single-setting comparison adapts only 395 annotated nonpatchy local cells, using the earlier strongest engineering setting (450 ms decay, 13.5 mV increment). Eight full-network trials compare original and candidate with no odor/left odor on two fresh diagnostic seeds. The candidate responds, recovers to the matched no-odor baseline and responds again; all tested recovery, burst, support and continuation checks pass. Individual PN/local recovery differences and signed DNa02 recovery differences are zero. The original retains high activity. Exact-cell physiological fits remain unavailable; right/bilateral/gradient cues, embodiment and learning remain untested. The live controller is unchanged. See LOCAL_RECOVERY_DECISION.md and local-adaptation-closed-loop-v1/RESULTS.md.

Separate single-input measurements refine the directional diagnosis: each selected PN favors its ipsilateral receptor population, but the left PN has a larger overall effective input scale for either receptor side. Side information therefore remains; raw PN subtraction can confound it with unequal gain. No fitted normalization or anatomical gain correction has been applied.

Frozen follow-up validation is now complete: 28 trials on two further fresh seeds cover none, left, right, full bilateral, 50/50, 60/40 and 40/60. The candidate passes all 24 response/recovery and all 24 late-burst checks, plus support and exact continuation. It fails all four original PN direction and all four gradient comparisons. Both unilateral cues produce positive PN contrasts; DNa02 outputs also favor the same signed direction. Motor-gradient alignment passes only 1/4 comparisons. All 6,720 chunks pass independent raw-spike/motor/clock checks and exact parity with the frozen evaluator. A controlled 60-chunk interruption reconstructs exactly. No controller is promoted. Read local-adaptation-direction-v1/RESULTS.md and DIRECTION_DECISION.md; the next work analyzes saved sensory-to-steering activity rather than widening adaptation tuning.

The next offline trace is complete and covers all 28 saved trials without new simulations. Exact DM1 receptor activity distinguishes both binary sides and unequal intensity. The sampled PN/KC/MBON32 pathway is nevertheless left-biased for either cue; switching to raw MBON32 subtraction would not solve the recorded gradient problem. Right DNa02 receives negative net accepted delivery in all 24 candidate odor-pulse observations, with one exact left AOTU019 supplying 45.6–56.0% of its inhibitory delivery. This is descriptive attribution, not proof that deleting that source repairs the recurrent brain. All 6,720 chunks rehash, independent last-spike event accounting checks 36,288 signed totals, and observed g/adaptation endpoints agree to numerical precision. Ten route targets lack independent state samples; two published relay labels have ambiguous compound annotations. No fitting, acceptance change or controller promotion occurs. Read sensory-steering-trace-v1/RESULTS.md and STEERING_TRACE_DECISION.md for the focused next checks.

The fixed-source follow-up is also complete: 28 intact four-recipient replays reproduce saved spike ticks/counts and sampled voltage/g, before 56 altered-input replays. An independent direct-event/closed-form audit checks all 336 recipient units exactly, without Brian2 or the native replay helper. Removing local/recurrent PN input still gives same-signed binary contrasts; its recovered-source gradient criterion satisfies only 2/4 comparisons on one reused seed. Removing paired AOTU019 delivery releases right DNa02 firing but does not restore opposed direction (0/4) or reliable gradients (1/4). Sources cannot respond to either intervention, so this is not a recurrent-network repair. Native analysis takes about 62 seconds with 0.90 GiB peak RSS. No production controller or acceptance criterion changes. Read receiver-counterfactual-v1/RESULTS.md and RECEIVER_DIAGNOSTIC_DECISION.md; the next comparison would test the recovered intact MBON32-to-descending route on fresh diagnostic seeds.

The follow-up intact-network capability comparison is complete: eight trials directly drive the exact left/right MBON32 roots at50Hz on two fresh diagnostic seeds, with two pulses and matched support-only controls. Target responses and renewed responses12/12, recovery12/12, support perturbation24/24 and late bursts12/12 pass; descending direction0/4 fails. Left signed output changes only2–6Hz and right pulse-average changes0Hz, though both sides' precise spike timing changes. All1,920 chunks, two whole-state continuations and a60-chunk interruption reconstruction pass independent checks. Importantly, none of the395 adapted local cells spikes in these odor-free runs: adaptation is not engaged, so this does not measure its effect during active sensory processing. The summary writer's NumPy-boolean failure was repaired only at serialization, without changing the40 pinned sources, graph or criteria or rerunning a simulation. Read recovered-mbon32-capability-v1/RESULTS.md and RECOVERED_MBON_CAPABILITY_DECISION.md. No controller is promoted.

The saved-run route/state audit is complete:36 parent recordings,8 intact DNa02 predictions and16 fixed-source edge-removal replays. Independent dense-event and closed-form checks reproduce all48 recipient units exactly and rehash8,640 chunks. The imported direct MBON32 links are inhibitory and unequal (40 versus10 sites).98–99% of unilateral direct arrivals are accepted; the weaker right link changes timing without changing pulse counts, while the stronger left link removes spikes. Odor-free pulses engage only1–2 of156 anatomical two-hop intermediates versus44–52 in local-adaptive odor pulses. This cross-archive comparison has different seeds and MBON refractory policies, so it does not prove a causal context/adaptation effect. A single matched context design is documented but has not run. Original direction failures and all39 requirement statuses remain unchanged. Read recovered-route-state-audit-v1/RESULTS.md, ROUTE_STATE_DECISION.md and SENSORY_CONTEXT_COMPARISON_SPEC_V1.md.

The committed progress files are snapshots, not live feeds. Raw recordings, derived profiles, receiver input/replay arrays and new capability-trial checkpoints needed to independently reproduce these checks remain excluded from the GitHub snapshot.

## What is established and what is not

- The full available modeled graph runs, with individual spike recordings and persistent state.
- Separate diagnostics verify selected checkpoint continuation and recording integrity.
- A local-only adaptation candidate passes recovery across the tested odor conditions; frozen directional and gradient criteria fail, so controller qualification remains incomplete.
- The application contains an arena, supplied locomotion, recording/replay and visualization machinery; the complete delivery workflow still has pending acceptance items.
- Useful sensory-dependent directional choice remains unresolved.
- Biological fidelity, successful embodied learning and a fully validated sensory-to-motor brain are not established.
- Tonic walking support, engineered escape behavior and synthetic sensory encoding must remain visible in explanations of gameplay.
- Colorful anatomy, movement, weight changes and a compelling video do not establish intelligence, learning or consciousness.

## Read these files

- `README.md`: application overview and limitations.
- `reports/provenance.json`: upstream versions, hashes and alterations.
- `reports/brain-integration/acceptance-ledger.json`: outstanding requirements.
- `reports/brain-integration/recovery/feedback-trace-v1/RESULTS.md`: persistent-activity reconstruction.
- `reports/brain-integration/recovery/adaptive-cell-reference-v1/RESULTS.md`: isolated adaptation checks.
- `reports/brain-integration/recovery/adaptive-domain-screen-v1/RESULTS.md`: completed failed fixed-point screen.
- `reports/brain-integration/recovery/adaptive-parameter-sweep-v1/RESULTS.md`, `gate-breakdown.json`, and `protocol.json`: completed failed sweep.
- `reports/brain-integration/recovery/adaptive-feedback-trace-v1/RESULTS.md`: attribution under strong adaptation.
- `reports/brain-integration/recovery/dm1-feedforward-diagnostic-v1/RESULTS.md`: isolated readout and native replay checks.
- `reports/brain-integration/recovery/POST_SWEEP_DECISION.md`: evidence-based next steps.
- `reports/brain-integration/recovery/local-source-qualification-v1/RESULTS.md`: exact-root source inventory and physiological limitations.
- `reports/brain-integration/recovery/local-recorded-drive-reference-v1/RESULTS.md`: continuing-input versus input-off isolated checks.
- `reports/brain-integration/recovery/dm1-unitary-reference-v1/RESULTS.md`: ipsilateral information and unequal effective PN input scale.
- `reports/brain-integration/recovery/local-adaptation-closed-loop-v1/RESULTS.md`, `protocol.json`, and `independent-audit.json`: completed positive recovery screen and its narrow scope.
- `reports/brain-integration/recovery/LOCAL_RECOVERY_DECISION.md`: next validation gates; no controller promotion.
- `reports/brain-integration/recovery/local-adaptation-direction-v1/RESULTS.md`, `protocol.json`, and `independent-audit.json`: completed frozen validation, successful recovery and retained directional/gradient failures.
- `reports/brain-integration/recovery/DIRECTION_DECISION.md`: prioritized offline route analysis and architecture boundaries.
- `reports/brain-integration/recovery/sensory-steering-trace-v1/RESULTS.md`, `paired-summary.json`, and `independent-audit.json`: completed retrospective representation/input attribution and its coverage limits.
- `reports/brain-integration/recovery/STEERING_TRACE_DECISION.md`: small receiver diagnostics and a conditional intact-network capability comparison before architecture changes.
- `scripts/trace_sensory_steering.py`, `scripts/audit_sensory_steering.py`, `flygarden/route_accounting.py`: frozen analysis and independent direct-event accounting.
- `reports/brain-integration/recovery/receiver-counterfactual-v1/RESULTS.md`, `protocol.json`, `native-validation.json`, and `independent-audit.json`: fixed-source native predictions and conditional input-removal results; no full-network repair.
- `reports/brain-integration/recovery/RECEIVER_DIAGNOSTIC_DECISION.md`: bounded intact-network capability comparison before selecting an architecture change.
- `scripts/diagnose_receiver_counterfactual.py`, `scripts/audit_receiver_counterfactual.py`, `flygarden/receiver_diagnostic.py`: frozen native receiver comparison, independent closed-form/dense-event audit and input partitions.
- `reports/brain-integration/recovery/recovered-mbon32-capability-v1/RESULTS.md`, `protocol.json`, `independent-audit.json`, `activity-coverage.json`, and `serialization-amendment.json`: failed intact-network direction, inactive-adaptation caveat and preserved output-only bug fix.
- `reports/brain-integration/recovery/RECOVERED_MBON_CAPABILITY_DECISION.md`: retrospective route/state-engagement diagnosis before another intervention.
- `reports/brain-integration/recovery/recovered-route-state-audit-v1/RESULTS.md`, `protocol.json`, `anatomical-inventory.json`, `native-validation.json`, and `independent-audit.json`: completed exact prediction, direct-edge diagnostics and descriptive operating-state comparison.
- `reports/brain-integration/recovery/ROUTE_STATE_DECISION.md` and `SENSORY_CONTEXT_COMPARISON_SPEC_V1.md`: one fixed future context design; no context run or controller promotion.
- `scripts/trace_recovered_route_state.py`, `scripts/audit_recovered_route_state.py`, and `flygarden/route_state_audit.py`: frozen analysis, independent raw/closed-form checks and tested event accounting.
- `scripts/test_recovered_mbon_capability.py`, `scripts/finalize_recovered_mbon_capability.py`, `scripts/audit_recovered_mbon_capability.py`, `scripts/summarize_capability_engagement.py`: frozen runner, output-only finalizer, independent raw checks and descriptive engagement accounting.
- `flygarden/directional_metrics.py`, `scripts/validate_local_adaptation_direction.py`, `scripts/audit_local_direction.py`: versioned validation and exact original-evaluator parity.
- `flygarden/brain.py`, `adaptive_neurons.py`, `adaptive_brain.py`, `adaptive_candidate.py`: baseline and adaptation implementation.
- `scripts/sweep_adaptive_lif.py`: frozen experiment runner and acceptance evaluation.
- `flygarden/continuous_candidate.py`, `candidate_inputs.py`, `descending.py`: sensory encoding and motor decoding.
- `flygarden/body.py`, `world.py`, `recording.py`, `server.py`: embodied application infrastructure.

## Questions for Muse

Please assess whether the explanations accurately separate Carson's project design, Codex's implementation, and upstream research. Examine whether the neural assumptions and acceptance gates support the proposed claims; identify concrete numerical, causal, reproducibility and usability problems. Suggest useful applications that fit the demonstrated capabilities. Treat missing raw data as unavailable evidence rather than inferring it from summary reports. Do not assume successful learning or consciousness.

## Repository scope

This is a source-and-evidence snapshot, not a backup of the complete local research archive. Large graph downloads, annotations with unresolved redistribution terms, morphology caches, raw spike recordings, videos, checkpoints, virtual environments, runtime state and dependency installations are excluded. No local recordings were deleted. Read `docs/REPRODUCIBILITY.md` and `docs/SHARE-MANIFEST.json` for what is included and excluded. Report links or hashes may refer to excluded artifacts; their inclusion in a report does not mean the underlying file is available here.

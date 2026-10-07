# Fly Garden: sensorimotor recovery and complete application acceptance

Planning document, 2026-10-06. This document does not start simulations, change the controller, or establish new biological results. It supersedes treating Step 9 as a simple move to harder arenas. Earlier failures and immutable recordings remain evidence.

## Objective and current evidence

Deliver a reliable local application whose controller identity, neural activity, behavior, recordings, and learning claims agree. Establish useful brain-dependent action selection before promoting obstacle navigation, escape, or learning. A connectome-based model may remain unable to reproduce the required behavior; the plan includes a truthful fallback rather than guaranteeing a biological outcome.

Step 8 completed 20 independent stochastic input/gait seeds, 60 full-brain/body trials, and 40 body-only controls. Sensory-dependent command changes and exact physical replays pass. Directional avoidance and useful movement fail. None of the twenty seeds reached the declared 0.05-radian away-heading or 0.1-mm departure targets; maximum departure was 0.029292 mm. Selected DNp09 cells emitted zero spikes; selected DNa02 cells emitted 98 across intact trials. These are stationary recorded-eye stimulus experiments, not live navigation tests.

The live Engine uses an older 100-ms adapter, tonic P9 stimulation, geometric threat features, and a supplied escape motor override. The experimental pipeline has verified causal 25-ms scheduling and body-state sampling. The two pipelines must not be conflated.

DNp09 silence in this cue protocol is a bottleneck for the chosen decoder, not proof of a defective biological circuit. DNp09 activation can produce state-dependent running/freezing; the original whole-brain reference was developed to test sensorimotor transformations, not to guarantee autonomous garden behavior. Use task-specific hypotheses.

## 0. Preserve evidence and define what each mode claims

Snapshot current application source, dependency versions, annotations, mappings, presets, and checkpoints. Preserve the existing runnable application and every old failed trial. Give new candidates immutable controller/encoder/mapping identifiers. Never change Stage 8 source hashes or retroactively weaken its thresholds.

Expose separate identities: supplied baseline; engineered hybrid with brain-dependent responses and declared walking/state support; and any subsequently validated connectome-based decision controller. The supplied gait generator remains declared in every embodied mode. Display tonic stimulation, sensory encoders, output overrides, plasticity, and model coverage in both UI and manifests. An intervention that is needed for a functioning hybrid is allowed only as a visible model component with matched controls.

Acceptance: a run can be traced from browser controller selection to actual neural inputs, decoder, motor timeline, source hash and report. A baseline or escape override cannot silently be labeled a validated brain decision.

## 1. Establish the body's usable command range independently

Use the verified physical sampler and fixed gait controller. Measure stopping, starting, straight motion, left/right turns, sustained motion and recovery on open ground. Sweep a small declared set of equal drives and turn differences on calibration seeds; then freeze the range and smoothing. Track actual displacement, yaw, contacts, falls, slips, active stalls, and settling. Repeat at the intended coupling interval. Test at least ten seeded 60-second reference runs.

Use injected rates only as a decoder/body diagnostic. Confirm units, motor clipping, direction conventions, gain and smoothing with actual body motion, not only arithmetic tests. Derive the minimum useful drive from measured body behavior; record it without presenting it as a biological firing threshold. Never amplify tiny neural fluctuations merely until a visual demo looks good.

Acceptance: zero, forward and mirrored turning commands produce the intended distinct physical outcomes; finite physics throughout; failures retained; sustained walking demonstrably possible under the chosen body configuration. If this fails, repair physics/gait before touching brain connectivity.

## 2. Diagnose each interface instead of treating all inactivity alike

Build a fixed diagnostic matrix: quiet state, documented reference stimulation, direct descending stimulation, odor cues, visual translation, looming, contact, and recovery. Include initial rest and an explicitly supported locomotor-state condition. Use short experiments and a few diagnostic seeds first.

Record input event counts, delivered currents, selected membrane potentials, excitatory/inhibitory contributions, intermediate spikes, descending spikes, decoded drive and actual motion. Audit exact root IDs, hemisphere, units, signs, ordering, refractory settings, stimulus amplitude, and reference deviations. A graph path is a hypothesis, not proof of functioning transmission.

Decision tree: no delivered events → adapter; events but no target response → stimulation/equation regime; target response but no downstream response → model/state/circuit hypothesis; descending response but insufficient commands → decoder mismatch; adequate commands but no motion → body interface. Preserve separate explanations where several failures coexist.

Acceptance: reproduce chosen released-model behaviors under their documented conditions and identify where each garden-relevant signal stops. Directly stimulated motor cells establish an output capability, not sensory-guided choice.

## 3. Choose a defensible locomotion and decision architecture

Reassess whether a fixed DNp09-forward / DNa02-difference decoder is appropriate for each task. Review primary functional evidence and the exact available annotations before adding or changing descending populations. Record why a candidate population represents the intended action and what is unknown.

Prefer a minimal, documented change supported by diagnosis. Possible candidates include revised sensory stimulation, state-dependent operating conditions, or a separately versioned population decoder. An optional tonic locomotor-state input must be explicit, applied identically across intact and frozen/sensory-off comparisons, and independent of food/predator coordinates. Direct motor override is a supplied behavior and must be evaluated separately. Never remove inhibitory connections as a production fix merely because a lesion increases firing.

Calibrate on a disjoint small seed set with a bounded parameter grid. Freeze the candidate before testing fresh held-out seeds. Do not select a candidate on final test results; a revision requires a new test set and retains the previous failure.

Acceptance: useful start/stop/turn behavior and sensory-dependent changes can coexist without hidden navigation. If only the declared hybrid works, deliver it as a hybrid and report autonomous full-brain behavior as unestablished.

## 4. Validate sensory channels separately

Odor: antenna positions and units, distinct channel identities, equal/mirrored exposure, zero exposure, dilution, adaptation/recovery where modeled, and food-contact timing. Record ORN, intermediate, mushroom-body and descending responses. Distinct sensory responses alone do not prove attraction.

Vision: actual left/right body cameras, orientation and coordinate checks, blank scenes, static dark objects, sudden appearance, translation in both directions, expansion, camera self-motion, occlusion and wall approach. The current dark-area expansion proxy is not a general navigation visual system. Diagnose its onset/translation false positives before adding obstacle tasks. Add optic-flow or other features only with a documented mapping; label engineered encodings and do not invent per-neuron receptive fields or retinotopy.

Touch/motion: retain raw physical signals as diagnostics when neural mappings are unsupported. For the supported ascending candidates, confirm delivered input and downstream action under defined contact conditions. A failed contact-to-retreat response remains failed; the supplied gait controller's contact correction is a different mechanism.

Acceptance: each encoder distinguishes its intended stimuli from chosen confounds on held-out cases, with matched sensory-off controls. Coverage, missing pathways and engineered components remain visible.

## 5. Integrate a genuine continuously updated loop into the application

Reuse the verified causal scheduler, continuous brain state, copy-safe observations and 30-Hz body sampler. Sample observations from the current physical body, encode them, advance neural state, and publish a new command for its next eligible interval. Hold the prior command over the interval that produced its successor. Update the visual scene from current world state. Do not feed recorded stationary clips to a controller labeled live perception.

Use one shared simulated clock for inputs, spikes, held motor commands, physics, world events and recordings. Preserve 100-us physics and 500-us gait dynamics; initially retain 25-ms neural coupling. Test shorter intervals only if an identified latency issue requires them. Rendering and playback are separate clocks. Slow computation slows wall-time playback, not simulated dynamics.

Resolve event granularity explicitly: collisions, moving predators, food contact and capture must use synchronized physical/world states and cannot skip crossings between coarse updates. Document event priority; capture wins over food in the same step. Pause/step/editor commands operate at defined boundaries; edits invalidate scored experiments.

Acceptance: future information never affects an earlier command; sensor changes follow actual body motion; sampling does not alter trajectories; fresh-process continuation reproduces every neural and physical state in the deterministic supported runtime; loading old checkpoints uses an explicit compatible version or migration.

## 6. Repeat causal tests on the frozen new candidate

Keep original failed Step 8 artifacts. Register a new protocol before running it. Include at least twenty matched seeded main trials balanced across cue sides, plus intact, sensory-off, targeted pathway interruption and exact motor replay controls. For hybrid candidates, add tonic-drive-only controls and keep state support identical across conditions. Use targeted interventions with exact masks and original signed weights; artificial interventions do not establish unique biological pathways.

Measure signed heading, useful displacement, speed, latency, active stalls, flips, neural response and command change. Retain all wrong-way turns and failures. Reuse Stage 8's original useful-response criteria where the task is the same; commit task-appropriate metrics separately for walking, odor orientation and threat response. Do not require every legitimate threat response to be a walking escape. Game escape success and biological response fidelity are separate checks.

Freeze sample size, trial duration, pairing, exclusions, bootstrap family correction and thresholds beforehand. Require positive paired effects relative to matched controls where a directional improvement is claimed; report counts, effect sizes and uncertainty. Twenty seeds are a minimum, not a guarantee of precision or twenty biological animals. A preplanned larger study may follow an inconclusive result without selectively discarding old data.

Acceptance: useful movement plus appropriate cue-dependent choices, causal controls and reproducible state. A response that passes only with an override earns a supplied/hybrid claim.

## 7. Progress through behavior in dependency order

Open ground: start, stop and local cue response. Orientation: mirrored odor/visual cue placement and stimulus recovery. Food: food contact and depletion with no danger. Obstacle: one block or wall, collisions and stalls, then reachable/unreachable food. Generalization: unfamiliar food locations and obstacle layouts. Threat: visible approach, threat removal and occlusion, then loss of sight and shelter. Combined game: collect food under danger with capture ending the trial and retained learning when enabled.

For each level, preregister engineering targets after body/arena calibration and before held-out evaluation. Report success and failure rates, travel, time, energy, captures, stalls, falls and uncertainty. Run matched controls and comparable supplied baselines. A baseline calibrates whether a challenge is physically achievable; it does not validate the brain. Ensure shelter occupancy alone cannot win a food objective. Predator navigation may access geometry, but fly inputs remain local.

Acceptance: pass the current level before opening the next scientific level. Gameplay unlocks and scientific validation remain separate. Preserve failure videos instead of choosing only successful clips.

## 8. Establish learning after non-learning behavior works

Audit the current plasticity rule against the intended published model. Resolve exact KC/MBON/DAN compartments, update directions, reinforcement units, bounds and spiking-to-reference variables. The current depression rule does not reproduce the cited feedback/prediction-error model; the separate reduced equation check does not validate full-network learning.

Freeze encoders, state support and decoder. Run acquisition, unrewarded preference probes with plasticity frozen, save/restart retention, reversal, unfamiliar locations, and then aversive association. At least twenty independent seeded initial states per condition: paired learning, frozen and shuffled reinforcement controls. Measure behavioral choice as well as population firing and actual weight changes. Match exposure/opportunity so motor changes or unequal access do not masquerade as learning.

Acceptance: the predefined paired preference improvement has a 95% bootstrap interval above zero relative to frozen controls; reversal shifts toward the newly rewarded cue; retention survives restarting. Report inconclusive/failed results. No game-score-to-plasticity shortcut, PPO substitution or learning badge based only on altered weights.

## 9. Make the brain viewer explain measured activity

Separate neutral anatomy from neuron activity. Exact-root morphology joins; explicit modeled/available/visible neuron coverage; unavailable shapes remain listed. Show actual spike flashes and 100-ms firing rates on a fixed cross-run scale, with an optional clearly separate baseline-relative view. Branches of one modeled electrical unit share its activity color. Do not synthesize electrical waves.

Use quiet, a unilateral diagnostic stimulus, recovery and a representative embodied run as fixtures. At chosen timestamps, manually compare sampled neuron IDs and browser values to raw spike windows, including bin edges and inactive cells. Neuron inspection shows ID, annotation, counts and history; a sensory/intermediate/descending overlay shows the causal chain and motor timeline. Regions need not change simply because world location changes: changes must follow sensory exposure and modeled state.

Acceptance: an inactive neuron is visibly inactive, active neurons and hemisphere are correctly mapped, rate values match raw records, and seeking/backward seeking reconstructs the same activity rather than leaving old highlights behind.

## 10. Preserve inspectable 3D runs and reliable automatic video export

Keep bounded compressed all-neuron spike chunks, 30-simulated-FPS body poses, arena geometry, sensory/motor/event timelines and a versioned manifest. Verify count parity with the monitor and recording-on/off seeded outcomes. Preserve raw recordings alongside complete checkpoints and MP4s; they serve different purposes. Free-camera recorded playback must use saved poses/geometry, not recompute the simulation.

Atomic finalization; interrupted runs playable through complete chunks and labeled incomplete. Durable export queue with queued/rendering/complete/interrupted/failed/retry states, one worker and progress. Simulate batches first, render afterward. Default 1080p/30-FPS normal simulated-time side-by-side arena/brain, consistent timestamps and identity labels; legacy runs visibly say neuron spikes are unavailable. Camera/population rerenders reuse the original recording.

Acceptance: stimulus/contact timestamps align across raw data, interactive playback and MP4 to within one video frame; the scientific log retains finer timing. Validate scrubbing and free cameras, inspect real frames/video, test restart/retry/failed trials and unavailable morphology. Preserve 2-GiB free-space reserve; pause cleanly, never auto-delete recordings or checkpoints.

## 11. Run product-level release acceptance

Cold launch from a stopped application through the real macOS launcher. Exercise actual browser controls: controller selection, start, pause, step, reset, editing, save learned parameters, full checkpoint, branch, resume, experiment batch, recordings, free camera, neuron selection, video viewing/download and rerender. Verify interrupted application/workers, disk reserve, malformed requests, unavailable skeletons and partial outputs. Immutable lineage/checkpoints must not be overwritten.

Run focused automated tests plus headless deterministic replay and actual native/browser checks; neither substitutes for the other. Promote the validated experimental loop into the application only after scientific gates and application regression checks pass. Deliver representative successful and unsuccessful recordings, provenance, tutorial and a feature-by-feature report: brain runtime; live sensory coupling; neural control; navigation; learning; morphology; playback; export; persistence. Each gets an independent working/limited/failed status.

## Compute strategy and stopping rules

One full-brain worker initially; no reduction of the network or silent skipped dynamics. Operate expensive batches on AC power. Measure short diagnostic runs before promising an ETA. Cache pinned data and reusable eye fixtures. Screen cheaply with body-only tests, reference checks and short neural runs; run large held-out batches only after an informative candidate is frozen. Keep batch/render resources separate and support safe interrupted-run continuation.

The completed Step 8 used approximately 3,845 seconds of full-brain/body arm computation and 781 seconds of body-only computation for 180 neural simulated seconds: about 77 minutes combined computation, excluding startup/interruption and report overhead. Peak worker RSS was 2.75 GiB and evidence approximately 505 MiB. This cue protocol is not a benchmark guarantee for live eye processing or 120-second challenges. Longer trials may take hours; estimates must use fresh measured throughput and actual planned arms.

Stop advancing behavior when a prerequisite fails; continue useful diagnosis rather than hiding the failure. Do not fit on final seeds, lower gates after outcomes, silently switch to a reduced model, or describe hybrid support as spontaneous brain competence. If the fixed reference cannot support useful choice after documented bounded tests, deliver a reliable engineered hybrid/baseline with full-brain recording and honest scientific limitations. Autonomous connectome behavior remains a separate unresolved result.

The next implementation package is phases 0–2: preserve/label controller modes, measure the actual body/decoder operating range, and run a short task-specific interface diagnostic. It should end with a measured diagnosis and a documented candidate decision before another large batch.

## Primary references

- Shiu et al. (2024), whole-brain computational sensorimotor model: https://www.nature.com/articles/s41586-024-07763-9
- Zacarias et al. (2018), state-dependent DNp09 running/freezing: https://www.nature.com/articles/s41467-018-05875-1
- Descending networks transform command signals into population motor control (2024): https://www.nature.com/articles/s41586-024-07523-9
- Existing measured evidence: stage8-20261006/RESULTS.md and stage9-20261006/RESULTS.md; local learning rule audit: ../../LEARNING_RULE_AUDIT.md.

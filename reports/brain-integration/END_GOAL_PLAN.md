# Fly Garden: complete delivery and scientific acceptance plan

Prepared 2026-10-06 from current local evidence. This is a planning artifact; it does not start new experiments or promote a controller. It supplements RECOVERY_PLAN.md and preserves its scientific gates and all failed results.

## End state

A local application with one persistent modeled fly in an editable 3D garden: foraging, obstacles, shelters, an engineered predator, controlled learning experiments, individual-neuron branching anatomy, inspectable free-camera recordings, automatic synchronized MP4 export, immutable learned-state and complete-scene checkpoints, and dependable launch/recovery.

The application must distinguish supplied control, engineered neural integration, and scientifically validated brain-dependent behavior. Full-brain navigation and learning remain experimental outcomes. A reliable baseline or hybrid release does not count as proving them. If a scientific prerequisite fails, preserve the failure, continue appropriate diagnosis and independent application work, and leave that scientific requirement unresolved.

## Current evidence

- Ten seeded 60-second physical-body acceptance trials passed; bounded restart and commanded movement were verified.
- Full modeled network: 138,639 neurons, 15,091,983 aggregated connection records and 54,492,922 anatomical synapses, as counted from imported artifacts.
- The latest odor protocol completed all 60 neural trials, independent data/decoder audits and 20 exact native physical replays.
- Odor changes motor commands causally. Directional orientation fails: only 10/20 meet the registered heading target; 16/20 is required. Both sides produce essentially the same turn bias.
- Actual-eye vision remains unresolved: early features confused self-motion with threats; later registration rejected true cues.
- Full-scene deterministic continuation passed bounded checks. The browser app still uses an older 100-ms adapter and supplied escape override.
- The activity seek race has a code fix and nine passing browser-code checks; visual acceptance remains pending.
- Current plasticity does not reproduce the cited prediction-error learning model. Learning is unvalidated.
- Recorded playback and MP4 infrastructure exist, but current research trials need integration and comprehensive release acceptance.

## Work sequence

1. Create a requirement-to-evidence ledger. Include every original garden, research, recording, viewer and delivery requirement, its prerequisite, objective pass criterion, evidence path and working/limited/failed/pending status. Completion requires direct evidence; a unit test cannot substitute for native dynamics or browser interaction.

2. Preserve the current release and experiments. Retain immutable source/dependency/data receipts, prior trials, checkpoints and failure recordings. Store code under version control going forward without adding huge data archives. Do not overwrite source-pinned historical candidates. Preserve a rollback launcher and separate runtime identities.

3. Audit the released full-brain reference. Reproduce selected documented stimulus-response cases using its original conditions, then compare the garden variant. Check imported cell/edge counts, transmitter signs, time constants, units, delays, reset rules, input jumps and refractory changes. List every deviation rather than claiming equivalence from matching neuron counts.

4. Build a complete odor-bias diagnosis from existing recordings first. Plot physical antenna concentrations, requested/delivered ORN stimulation, population sizes, intermediate activity, both DNa02 outputs, support activity, decoded drive and measured yaw against the shared clock. Separate rest, onset, cue exposure, cue removal and recovery. Distinguish unilateral firing from symmetric firing decoded asymmetrically.

5. Check the spatial and identity conventions. Verify antenna names, left/right neuron roots, stimulus column order, neuron ordering, world/body coordinates, yaw sign and decoder turning direction. Mirror a source and compare actual local exposures. Test both odor identities, both sides, equal bilateral exposure and no odor. Do not assume changing odor location must reverse a biologically unspecified preference.

6. Separate sensory encoding from circuit responsiveness with small new diagnostics. Use disjoint diagnostic seeds and matched support. Compare delivered unilateral/bilateral stimulation and naturally sampled local fields; measure target voltage, inhibition/excitation, intermediate and descending responses. Keep direct descending stimulation as a capability diagnostic, never as evidence of odor navigation.

7. Test the locomotor operating state as a possible cause. Examine support-only turning, bilateral support recruitment and onset/recovery. Reassess the physiological interpretation of P9 support. Only use a prospectively bounded, evidence-justified support revision; record all cells it stimulates and apply it identically in matched comparisons. No blanket inhibitory lesion or cue-driven walking override.

8. Select the action architecture explicitly. First attempt a justified sensory/state/descending repair within the full network. If evidence calls for additional annotated outputs or an engineered readout, version and disclose it. Readout inputs may use measured neural activity and documented local feedback; they cannot receive source coordinates, cue-side labels, predator positions or paths. An added controller must not silently replace the full brain. A larger engineered navigation adapter requires a clear scope decision.

9. Register calibration and validation before runs. Reserve separate calibration, diagnostic, held-out and later learning/generalization seeds. Declare parameter bounds, candidates, intervals, trial duration, sample size, exclusions, controls and statistical families. Keep prior thresholds for repeated tasks. Add prospective bearing error, source approach and distance-progress metrics where needed; yaw alone is insufficient evidence of navigation.

10. Calibrate a small bounded candidate and freeze it. Use short screens, select by the registered rule and retain failures. Freeze sensory mappings, support, decoding, smoothing and gait. No fitting on held-out outcomes or subtracting the observed left bias merely to make the evaluation pass. Every revision needs fresh validation seeds.

11. Re-run odor causal acceptance. At least 20 matched independent stochastic seeds, balanced sides and appropriate odor identities, with intact, sensory-off/support-only, targeted interruption and exact motor replay controls. Include two-cue discrimination separately from source orientation. Retain wrong-way turns. Require registered useful direction, movement, finite stable physics and uncertainty gates before promoting orientation.

12. Build a physical-eye vision test library. Preserve raw images, camera calibration, units, local body pose and fixture identities. Cover blank scenes, static objects, appearance/disappearance, mirrored translation, expansion/shrinkage, occlusion, wall approach, own legs, turning and translation. Hold out object shape, texture, angle, speed, background and trajectory. Labels belong to evaluation, not neural inputs.

13. Repair vision using only available observations. Diagnose both false detections and rejected true cues. Own-body masking, image features and documented proprioceptive compensation may be engineered components. External segmentation IDs, world object coordinates and privileged motion cannot become fly sensory inputs. Audit mask geometry and numerical camera conventions without altering physics.

14. Define visual-to-neural mappings conservatively. Identify exact annotated target populations and published functional support. Declare uniform stimulation where used; do not invent per-neuron receptive fields. Distinguish expansion, translation and optic-flow channels only when mappings support them. Freeze the encoder before held-out specificity/sensitivity tests and subsequent neural response evaluation.

15. Validate touch and body-motion channels independently. Use actual solver contacts and anatomical sites; distinguish stumbling corrections, ground loads and adhesion. Resolve ascending mappings before claiming neural feedback. Unsupported signals stay diagnostic. Test delivered events and downstream action under defined contacts with matched control conditions.

16. Consolidate the continuous simulation implementation. One canonical coordinator owns neural, physics, gait and world clocks. Retain 100-us physics, 500-us gait and initially 25-ms neural coupling. Current senses generate a future eligible command; the prior command acts during that interval. Keep event crossing detection, capture precedence and terminal-step policy explicit. No skipped dynamics to maintain animation speed.

17. Establish longer-run and checkpoint parity. Extend bounded proofs to quiet, stimulated, food-contact, obstacle and threat states. Save neuron state, delayed spike queues, synaptic weights, eligibility, decoder smoothing, body/solver/gait, world, sensory histories, clocks and all random generators. Fresh-process continuation must match at every declared boundary within the supported pinned runtime. Cross-version loading requires compatibility handling, not a false exactness claim.

18. Integrate the new loop into a versioned research application mode. Preserve legacy/baseline modes and paused user state. Expose support, encoder, gait, overrides, learning and validation status. The same coordinator runs headless experiments and interactive trials. Protect live state with a full checkpoint before any service migration; no destructive restart to install a new mode.

19. Make resource ownership durable. Unify server commands, experiment jobs and external scripts around the actual native-worker lock. Permit playback during experiments, but reject conflicting model mutations. Validate process identity, clean cancellation and stale-owner recovery. Simulation batches finish before video rendering competes for resources. Compute is allowed on battery by user authorization; use measured safe concurrency, not an AC gate.

20. Validate world mechanics before brain competence. Test arena editing, spawn validity, walls, blocks, shallow terrain, contacts, food depletion, unreachable food, simplified energy, trial limits and reset. Test simultaneous capture/food, crossing events, interruption and edits invalidating scored evaluations. No teleportation to conceal falls or stalls. Default challenge duration is 120 simulated seconds.

21. Establish foraging in dependency order. Open-ground local response, mirrored orientation, one food source, multiple cue identities, choice without immediate reward, one obstacle, then unfamiliar layouts. Use supplied baseline controls to prove physical achievability. Register success targets after arena calibration and before evaluation; report collection, bearing/distance progress, time, collisions, stalls, falls and failures.

22. Implement and validate the engineered predator. Finite range/FOV/unblocked line of sight; bounded motion; patrol, pursuit, search and return states; last-seen position after visibility loss; obstacle-respecting navigation. Predator geometry access is permitted only for predator control. Shelters must genuinely occlude and allow fly entry/exit. Capture ends the trial and retains learning when enabled. Any supplied escape behavior has a visible identity and matched controls.

23. Evaluate threat and combined tasks progressively. Visible approach and disappearance first, then occlusion, shelter, loss of sight and dangerous foraging. Distinguish immediate avoidance, supplied escape and learned cue avoidance. Calibrate physically achievable difficulty on separate baseline seeds. Shelter occupancy alone cannot satisfy a food objective. Scientific unlocks require their gates; gameplay achievements do not substitute for them.

24. Resolve the learning model before full-network training. Use the pinned published equations/source as a reference. Audit exact KC/MBON/DAN compartments, action-valence mapping, signs, potentiation/depression, bounds, reinforcement units, eligibility and dopamine feedback. State which aspects are reproduced and which are a new spiking approximation. Preserve the current failed depression-rule evidence. No PPO, GA or game-score reinforcement substitute.

25. Validate the learning mechanism in layers. Check reduced reference equations, then mapped full-network cue responses, actual compartment reinforcement, signs/bounds and pre/post weight changes. Only designated plastic connections may change. Non-learning weights and decoding remain fixed. Freeze candidate adaptation after disjoint calibration; mechanism checks do not establish behavioral learning.

26. Run prospective behavioral learning acceptance. At least 20 independent initial stochastic states per paired, frozen and shuffled condition. Match exposure/opportunity; acquisition followed by unrewarded frozen-plasticity probes, restart retention, reversal and novel locations/layouts. Use the predefined paired preference improvement confidence criterion and reversal requirement. Test aversive conditioning before associating capture with reinforcement. Failed behavior stays failed even if weights move.

27. Complete persistent-fly semantics. Separate ordinary trial reset, learned-parameter save and full-scene checkpoint. Trial reset clears transient state while retaining learning; complete checkpoints preserve continuation. Branch only from immutable verified checkpoints, record lineage and never overwrite ancestors. Allow branch comparison without making identity or consciousness claims.

28. Unify raw recording formats and import preserved research runs. Store exact root ordering, compressed bounded all-neuron spike chunks, 30-Hz poses, arena/body geometry, sensory inputs, held/next motor commands and events. Include controller/mapping/source/dependency/seeds/learning identities and checkpoint links. Preserve run completeness. Importing saved trials must not rerun the brain or invent missing neural state; recover an initial physical pose only through a source-verified procedure when necessary and mark its provenance.

29. Test raw recording invariants and interruption recovery. Count parity with monitors; seeded recording-on/off parity; quiet windows with no poses; chunk edges; checksum failure; partial files; metadata atomicity; interrupted writer; low space and resume. Ignore uncommitted orphan chunks without deleting them. Maintain a 2-GiB free-space reserve and never automatically delete archives or checkpoints. Video and recording seeking are not checkpoint restoration.

30. Finish anatomical coverage and efficient geometry. Exact FlyWire 783 root joins, consistent units/alignment and source/cache hashes. Sample representatively before estimating full-cache size; previous targeted size estimates are not reliable full-cache forecasts. Download progressively and resumably, prioritize selected/active neurons, and offer broader cache acquisition after measured space/runtime checks. Keep modeled, available, cached and visible counts separate. Missing morphology stays listed. Confirm redistribution terms before shipping geometry. Simplification affects presentation only.

31. Verify neuron activity and inspection quantitatively. Neutral inactive anatomy; actual spike flashes; preceding 100-ms rate on fixed cross-run 0–500+ Hz scale. One activity value colors all branches of a modeled neuron. Compare selected raw IDs and browser rates at quiet, unilateral stimulus, recovery and embodied timestamps, including exact bin boundaries, future exclusion, rapid seeks and reverse seeks. A loading state cannot reuse stale activity. Show annotations, counts, history, coverage and causal sensory/intermediate/descending/motor timelines.

32. Finish free-camera recorded playback. Saved poses/geometry drive replay without physics or neural recomputation. Test pause, speeds, end/restart, forward/backward scrubbing, event jumps, overhead/follow/free cameras, orbit/pan/zoom and saved viewpoints. Arena and brain read the same recorded timestamp. Legacy recordings explicitly indicate absent individual activity. Separate illustrative markers from scientifically recorded events.

33. Complete durable automatic export. Queue every newly recorded trial, including unsuccessful/interrupted playable trials. One renderer shares the Three.js presentation and reads the original data. Default 1080p/30-FPS normal simulated-time arena/brain layout with time, simplified energy, food, outcome, controller, learning and activity legend. Persist queued/rendering/complete/interrupted/failed jobs, progress and retry. Publish MP4 through temporary files; retain recordings on every failure. Rerender cameras/populations without neural recomputation.

34. Prove playback/video synchronization and resource recovery. Known input/contact/capture markers must align within one video frame; scientific logs keep finer timing. Inspect real beginning/middle/end and failure clips visually. Test export/application crash, FFmpeg failure, retry, missing skeletons, legacy runs and low space. Record actual encoder frame rate/resolution/duration, peak memory, output size and render time.

35. Finish the approachable application experience. First viewport: arena, play/pause, simulated time/speed, energy, food and status. Laboratory panels expose sensory/motor/reinforcement activity and actual throughput. Recordings list outcome, duration, completeness, coverage and export state. Editor pauses and records scored invalidation. Provide Sandbox, Challenges and Experiments with tutorials and honest separate gameplay/scientific badges. No fear meter or consciousness score.

36. Benchmark and optimize without changing the scientific model silently. Profile setup, full-brain dynamics, cameras, physics, serialization, UI and export separately. Remove measured avoidable copies and bound queues/caches/recordings. Test faster numerical backends or multiple workers only as versioned parity-checked candidates. Benchmark 10 simulated seconds of brain, body and combined operation and target total application memory below 10 GiB. Call execution live only when measured combined throughput is real time and controls remain responsive; otherwise retain asynchronous computation and recorded playback. Keep the full available network; reduced modes require a scope decision. Start from one worker, measure two-worker performance/memory before wider concurrency and avoid swapping. CPU authority is broad, but fabricated throughput gains are not acceptable.

37. Run adversarial operational acceptance. Malformed requests, conflicting commands, interrupted jobs, dead owners, disk reserve, missing annotations/skeletons, corrupt chunks, incompatible checkpoints, duplicate exports, unreachable food and simultaneous terminal events. Verify loopback binding, local API access controls, bounded request sizes and owned-process shutdown. These checks cover concrete local application behavior rather than hypothetical warnings.

38. Rehearse delivery from a stopped application. Save current state, stop only owned services, launch through the real macOS launcher and exercise the actual browser workflow. Test mode selection, run/pause/step/reset, arena editing, learned/full saves, branches, restore, experiment batch, recordings, neuron selection, free cameras, viewing/download and rerender. Repeat restart with interrupted work. Unit/API checks supplement this; they do not replace it.

39. Publish the evidence package and completion ledger. Deliver pinned dependencies/provenance/licenses, tutorials, reproducible presets, benchmark/storage report, representative successful and unsuccessful recordings and MP4s, immutable checkpoints and lineage examples. Separate status for full-brain runtime, senses, neural movement, direction/navigation, learning, predator gameplay, morphology, replay, export and persistence. Mark the full goal complete only if every explicit requirement has adequate evidence or an explicitly accepted revised scope; do not label an unproven scientific aim achieved by delivering a smaller demo.

## Execution packages and gates

- Package A: steps 1–11, odor-bias/reference diagnosis and a frozen orientation candidate. End with a measured decision, not another blind long batch.
- Package B: steps 12–19, validated sensory encoders and versioned application integration. Recording/viewer work can proceed independently where it does not interfere with native workers.
- Package C: steps 20–23, validated world mechanics and progressive behavior. Scientific levels stop at failed prerequisites; supplied baseline gameplay can still be assessed honestly.
- Package D: steps 24–27, mapped plasticity, controlled behavioral learning and persistent lineage. Do not spend a large learning budget before non-learning task behavior is useful.
- Package E: steps 28–35, faithful records, neuron viewer, free-camera playback, exports and complete interface. Preserve failed experimental runs as usable teaching/inspection artifacts.
- Package F: steps 36–39, optimization, failure recovery and actual cold-launch release acceptance.

## Compute and decision policy

The user authorizes compute on battery and at all times. Do not restore an AC-only restriction without a new instruction. Keep the storage reserve. Benchmark concurrency rather than assuming more workers are faster or safe for a 16-GiB machine.

The current active odor arms took roughly 42–46 wall seconds for 3 simulated seconds, excluding some startup overhead: approximately 14–15 wall seconds per simulated second. A 120-second trial extrapolates to roughly 28–30 minutes at that rate; 60 such trials would be roughly 28–30 hours of computation. This is an estimate, not an ETA: visual workload, firing intensity, checkpoints and learning can change it. Use short informative screens and fresh measurements before long batches. Rendering remains separate.

For each failure: first check implementation integrity, then analyze operating state and task assumptions, then revise one justified component on calibration data, freeze, and use fresh held-out data. Do not treat an anatomical asymmetry as a software bug without evidence. Do not tune old test seeds until success or silently replace the connectome with a navigator.

## Reference and evidence pointers

- Current causal result: recovery/odor-causal-v2/RESULTS.md, results.json and motor-replay-results.json.
- Current implementation status: recovery/progress.json; previous plan: RECOVERY_PLAN.md.
- Learning rule audit and pinned authors' equations: ../LEARNING_RULE_AUDIT.md and vendor/mushroom-body-rpe at revision 7ec52afb9bd7bb748d94d60dea9f483645a2ce8e.
- Motor architecture evidence: recovery/ARCHITECTURE_EVIDENCE.md.
- Physical/sensory interface reference: https://neuromechfly.org/ . Keep the installed pinned API distinct from current upstream documentation.
- Exact-version skeleton retrieval documentation: https://fafbseg-py.readthedocs.io/en/latest/source/generated/fafbseg.flywire.get_skeletons.html .

## Scope retained and later work

One persistent walking fly, full modeled network attempted first, plasticity before PPO/GA, 3D garden, capture ending the trial while retaining learning, and default project/media storage under /Users/carsonhicks/FlyGarden with a configurable alternative. RallyAI3 remains independent. No arbitrary archive cap or automatic cleanup. Flight, climbing, water, destructible terrain, weather, rich fluid plumes, population evolution and multiple predator strategies remain later additions; they are not substitutes for completing this walking-based release. Biological validation against observations is required before stronger fidelity claims.

Completion note: all 87 trials and the independent upstream check are now complete. See [the final diagnosis](DIAGNOSIS.md). The following is the preserved interim report.

# Stage 2 — partial diagnosis, paused for storage

41 of 87 planned full-network trials are complete. All 820 committed windows and 27,251,933 individual spikes passed hash, timestamp, finite-state and per-neuron count checks. Learning stayed frozen. The measurement counters passed full-network non-interference and two-cell signed-delivery/refractory tests. The live controller, previous recordings and checkpoints remain unchanged.

## Findings established so far

- Quiet trials produced no spikes. Brief walking and looming stimulation ceased after input removal.
- Switching odor A to B switches the corresponding sensory-neuron response.
- A 300 ms odor pulse leaves approximately 480,000 network spikes per second after external input stops. In the held-out seed, 8,244 of 138,639 neurons were active in the recovery tail. The entire network is not firing.
- Persistence remains under selected-input and ordinary 2.2 ms refractory conventions. Reducing the input voltage jump to 20% also retained persistence in the two completed calibration seeds.
- Paired odor-A/B gamma-Kenyon-cell rate vectors have cosine similarity 0.9989–0.9991 in the current adapter: very similar rate patterns, with small measurable differences. This metric is not a learning or consciousness score.
- DNp09 left/right neurons, which currently supply the walking readout, emitted zero spikes during these isolated odor probes.

Sensory input has a real effect, but useful sensory-driven movement is unproven. Persistent post-odor activity points to recurrent dynamics. The recurrence-off controls have not yet completed, so that causal diagnosis is not formally closed.

## Still required

Finish 46 remaining trials: lower-amplitude probes, rate-dose probes, recurrence-off controls and longer recovery. Then independently confirm recovery using the original upstream PoissonInput implementation, verify all artifacts, and produce diagnostic figures. No calibration profile has been promoted.

## Resource blocker and continuation

The filesystem repeatedly dropped below the agreed 2 GiB free-space reserve. Completed diagnostic evidence occupies about 109 MiB. macOS also reported about 30 GiB of memory swap in use. Available space continued changing while all diagnostic workers were stopped. The live application was paused, and its export queue contained no queued or rendering jobs when checked. No recordings or checkpoints were deleted to make room.

Continuation is prepared in `scripts/resume_activity_diagnostics.py`. It preserves completed trials and first reproduces one saved odor trial to verify exact spikes and matching sampled neural state. That equivalence check has not completed: the storage guard stopped the worker before recording. Each unfinished independent trial uses a fresh full-network worker to reduce retained memory; continuous neural state is preserved throughout each trial. Raw recording resumes only when sufficient space is available.

Evidence is retained in `protocol.json`, `progress.json`, `neuron-selection.json`, and the complete folders under `trials/`. Earlier setup failures and the storage interruption are retained separately and excluded from completed-trial counts. The partial verification was run with `scripts/report_activity_diagnostics.py --partial`; a complete report is intentionally not published while required tests remain unfinished.

# Stronger adaptation sweep

This preregistered engineering screen tests 50, 150 and 450 ms adaptation decay with 1.5, 4.5 and 13.5 mV spike increments. The larger values deliberately test whether stronger self-limiting activity can overcome persistent network firing without erasing responses. They are not fitted biological constants.

Two domains are tested independently: annotated projection neurons, and projection neurons plus explicitly annotated olfactory receptor neurons. Uncertain local-cell types and global adaptation are excluded from this sweep. Local inhibition, synapse signs, graph structure, input encoding and motor decoding remain unchanged. Learning is frozen.

Each of 18 adaptive arms and the original baseline receives four cue conditions on calibration seeds 12001 and 12002. A separate zero-adaptation regression makes 153 initial trials. Every left-cue trial receives fresh-process checkpoint continuation. The full grid runs without interim pruning or tuning. All response, recovery, contrast, burst and support gates remain fixed from the preceding screen.

The first candidate passing all gates on both calibration seeds is chosen using the frozen domain/step/tau order. It then receives 28 baseline/candidate trials on fresh held-out seeds 12111 and 12112, including mirrored 60/40 intensities. Passing this screen is insufficient for application promotion: embodied movement, escape and later learning validation remain separate.

One full-brain worker owns the experiment lock. Each trial writes atomic compressed chunks and preserves recordings. The 2 GiB free-space reserve is enforced. Complete trials can be reused after restarting; interrupted trials are preserved and require explicit recovery rather than being overwritten.

Expected initial runtime: about 2–3 hours based on the preceding roughly 50-second trials, with additional checkpoint and audit time. Actual runtime may change at stronger parameter settings. Follow progress.json, current-worker.json and run.log. No candidate is deployed automatically.

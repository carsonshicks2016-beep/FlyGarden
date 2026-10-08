# Recovered intact-network direct-MBON32 capability comparison

Eight preregistered full-network diagnostic trials: recovered local-only adaptation, two fresh diagnostic seeds 12401/12402, support-only / left / right / bilateral direct stimulation, six simulated seconds each. Fixed 50 Hz MBON32 input and 65 Hz bilateral walking support; no odor, vision, body or learning.

The original graph, signed weights, local-adaptation setting and descending decoder stay fixed. The two exact MBON32 roots are additionally zero refractory **in every case, including support-only**, matching the historical direct-drive convention. This differs from the odor-only candidate state and is an explicit engineering protocol change. The earlier original-model failure is historical evidence, not a matched fresh control.

All criteria, pulse/recovery windows, roots, sources and seed reservations are in protocol.json. Direct-input capability cannot replace failed original PN direction/gradient gates. Response, renewed response, recovery, bursts, matched-candidate support retention and descending direction are reported separately. No controller is promoted even if the diagnostic passes.

Use one simulation worker because the current Mac has roughly 4 GiB available and 4 GiB existing swap. Record all full-network spikes, requested and generator-delivered direct events, unchanged support events, endpoint states and motor commands in immutable compressed chunks. The 2 GiB free-space reserve applies; nothing is automatically deleted.

Both left trials receive a full checkpoint at 3.775 simulated seconds and a fresh-process five-window continuation comparison. One owned right-trial worker is deliberately interrupted after at least 60 complete chunks; its immutable prefix must reconstruct exactly before appending. An independent raw-spike/RNG/clock/motor audit and a plot run automatically after all eight trials.

Run locally with `.venv-next/bin/python scripts/test_recovered_mbon_capability.py` after the registration is committed and published. The same command resumes existing evidence; it verifies source hashes, skips complete trials and reconstructs interrupted prefixes without overwriting complete chunks.

Prelaunch checks: 13 focused input-schedule, paired-generator, restart-state, capability-metric, descending-metric and candidate-input tests passed. No full-network trial ran before this registration. Progress files are local live telemetry and become historical snapshots on publication. Underlying trials and checkpoints stay excluded from the public repository.

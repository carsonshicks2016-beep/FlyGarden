# Live integration and restart checks

The research loop now samples actual physical antenna positions and actual eye images, advances the full neural network continuously, and applies each newly computed motor command in the following25ms interval. Physics uses100us steps and the supplied gait/world loop uses500us intervals. The legacy public application has not been switched to this controller.

The reusable immutable scene save/load implementation passed three fresh processes: uninterrupted0–200ms versus an interruption at100ms and restart. At every25ms boundary, all Brian full-state objects, delayed queues, neural RNG/decoder, body physics/gait, world entities/events, visual baseline/history, raw spikes and playback records matched exactly. The fixture includes food contact, food depletion and retention of the event. This is bounded continuation evidence, not long-term navigation validation.

Native body observer parity separately passed200 world callbacks: full physics/gait snapshots and30Hz body poses matched the frozen body exactly. Scene loaders reject changed identities, interrupted saves and corrupted payloads before neural loading; checkpoints remain immutable.

A short-window recording defect was fixed:25ms intervals without30Hz poses now retain their individual spike chunks. Empty bounded windows also retain timing. Focused tests passed.

The native-image visual audit reconstructs all saved features exactly. Blank images remain silent; removal yields zero rates. Sudden static appearance produces100Hz false expansion in the relevant eye. The translating pattern peaks at100Hz on appearance and6.38Hz during subsequent motion. Looming produces sustained intended-side response. Thus visual specificity is FAILED, and self-motion, occlusion and held-out image fixtures remain missing. This encoder is not accepted for obstacle navigation.

All proof directories retain protocols, hashes and source snapshots. Scientific navigation, contact-driven choices and learning remain unvalidated. Next work is versioned visual encoding repair and its confound fixtures, followed by frozen-controller causal trials and application integration.

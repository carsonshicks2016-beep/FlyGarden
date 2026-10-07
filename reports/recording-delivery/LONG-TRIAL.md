# Longer recording and event timeline

The completed diagnostic is run `fe09e4c9440d465facffed398f95ee34`, seed 801: full 138,639-neuron network, frozen plasticity, food and the level-2 interior obstacle plus arena boundaries. It ran for 30 simulated seconds, with no falls or non-finite physical values. The scheduled recording boundary is not a gameplay success.

Saved 901 poses and 14,678,253 spikes. All 301 chunk hashes, event ordering, per-neuron totals, monitor counts and pose clocks passed validation. Pose spacing never exceeded 33.5 ms. Compute took 214.94 wall seconds, the simulation process peaked near 2.0 GiB RSS, and its recording occupies about 57.9 MiB. These are measurements of this one diagnostic, not a throughput guarantee or total application-memory measurement.

Playback now provides clickable timeline markers, an event menu and Previous/Next navigation. Clicking pauses at the saved event time and preserves a free-camera viewpoint. This run contains odor-A exposure at 0 s, odor-B exposure at 3 s, obstacle proximity at 3.7 and 4.5 s, and its scheduled boundary at 30 s. Food contact, reinforcement and capture markers appear when recorded; this run had none. Odor/range/threat thresholds are engineered display criteria. A real previously recorded capture was independently checked at 0.1 s. Committed-frame boundaries exclude interrupted tails.

The actual browser was exercised for marker jumps, scrubbing, neuron inspection, free camera, and selection. PPL101 root 720575940621040737 had 13,354 total spikes; its full-run firing history is available. The fly and brain read the same recorded clock.

Visual inspection exposed a late-run wall obstruction in the initial follow-camera export. Follow now chooses a clear observer-camera side. Physics, fly sensory occlusion, recorded poses, neural activity, and saved free viewpoints are unaffected. The original export is retained; a new export uses the corrected camera. Each renderer snapshot includes the camera helper and hashes.

The fly collected zero food. During 10–30 s its XY position spans only about 0.25 by 1.03 mm and net displacement is approximately 0.014 mm. Accumulated travel and the existing zero-stalls counter therefore do not demonstrate useful navigation. This recording is evidence of the controller's current limitation, not learning. The controller and plasticity equations were not changed.

37 Python tests and 7 JavaScript tests passed. The interrupted first diagnostic is retained and clearly labeled; its physics-check property error was corrected before the complete run.

To repeat: Learn → Reproducible experiments → Record full-brain obstacle trial · 30 s. Each repeat receives a separate recording and export. The original complete scene was restored and left paused at 37.9 simulated seconds.

- [Interactive playback](http://127.0.0.1:8794/static/recordings.html?run=fe09e4c9440d465facffed398f95ee34)
- [Corrected follow-camera MP4](../../data/exports/8e2276bb51c248859055fd0e13ca1207/video.mp4)
- [Raw recording](../../data/runs/fe09e4c9440d465facffed398f95ee34/manifest.json)
- [Integrity verification](obstacle-verification.json)
- [Trial measurements](obstacle-trial.json)
- [Behavior measurements](obstacle-behavior.json)
- [Tutorial](../../RECORDING-GUIDE.md)

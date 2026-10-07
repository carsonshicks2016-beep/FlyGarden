# Recorded brain delivery

Implemented in /Users/carsonhicks/FlyGarden. RallyAI3 is unchanged.

## Verified capabilities

- Full-model individual spike recording: all 138,639 modeled neurons are eligible for recording; the three-second diagnostic retained 1,447,028 spikes and 91 physical poses. Recording enabled/disabled matched seeded spike counts, voltages, motor commands and learned weights exactly, including a reinforcement step.
- Anatomical viewer: real FlyWire v783 skeletons joined by exact root ID. 365 matching skeletons cached (136,626,312 source/cache bytes reported by API), with no unavailable IDs among this fetched subset. Interactive loading proceeds in batches of 128; default videos show up to 256 selected skeletons. This is partial morphology coverage, not a complete brain geometry download. All other recorded spike events remain available.
- Synchronized playback: physical poses, neural events, inputs, reinforcement and world events use the simulation clock. Browser scrubbing and neuron selection were exercised. Selected PPL101 root 720575940621040737 showed 1,313 total spikes and 450 Hz at three seconds, independently checked against raw events.
- Automatic MP4: 1920 x 1080, H.264, 30 FPS. Completed both batch trials, including physical capture. A deliberately interrupted writer recovered after server restart and exported successfully. A camera/population rerender completed without recomputing the brain. Latest full-brain scene clip decoded successfully and was visually inspected.
- Persistence: raw recordings and immutable checkpoints retained; jobs persist and retry. Low-space protection keeps a 2 GiB reserve. No automatic archive deletion or cap.

## Measurements and limits

The three-second embodied full-brain diagnostic took about 19.7 wall seconds; its default video rendered in about 82.9 seconds after anatomy preparation. Runtime depends strongly on compilation, geometry selection and cache warmth. The latest 0.1-second full-brain clip rendered in 33.8 seconds after anatomy preparation. These are short diagnostic measurements, not real-time performance claims. The full-brain parity process peaked near 2.45 GB RSS.

The representative 16-skeleton sample suggested roughly 78 GiB for a full cache, but the sample is biased and this is a rough estimate. No bulk download was started. Skeleton retrieval provenance, hashes, native nanometer coordinates and identity transform are recorded. A standalone redistribution license has not been established, so the cache remains local with source attribution.

33 Python tests and 5 JavaScript tests passed. Checks cover chunk boundaries, incomplete writes, unavailable morphology, disk reserve, retries, restart recovery, pose sampling and seeded parity. Browser playback, selection, camera choice and export controls were exercised. A short acceptance batch is not a long-duration training validation.

The controller and learning rules were not changed. Learning remains unvalidated. Branches share each point-neuron model's activity; no electrical propagation is invented. Seeking an MP4 does not restore modeled state. The original complete scene was restored and left paused at 37.9 simulated seconds.

## Open these

- Tutorial: [RECORDING-GUIDE.md](../../RECORDING-GUIDE.md)
- Representative automatic fly + brain clip: [video.mp4](../../data/exports/5540318bc3fd4b7396f916dfeedf431b/video.mp4)
- Latest scene clip with frozen renderer sources: [video.mp4](../../data/exports/f60a2db888554028b4992625f002901e/video.mp4)
- MBON / overhead rerender: [video.mp4](../../data/exports/491d11d2925a425ea0c5e349d965d9ba/video.mp4)
- Browser proof: [playback-browser.jpg](playback-browser.jpg)

The local app remains at http://127.0.0.1:8794/. Choose Recordings, inspect a trial, scrub, select a neuron, or watch/download its MP4. Begin/new trial uses the unchanged existing controller. Finished and interrupted nonempty recordings queue exports automatically; experiment batches finish simulation before rendering.

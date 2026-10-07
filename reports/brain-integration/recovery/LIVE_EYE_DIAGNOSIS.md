# Live eye diagnosis

Two body/world command replays exactly reproduce all120 recorded boundaries per seed, every30Hz pose, and the original eye features. Full neural computation was not repeated. Fresh RGB images reveal that the v2 largest-component encoder often tracks the fly's moving legs instead of the visual object. The right-side v2 response is therefore not accepted as threat-specific.

A separate v3 prototype adds an engineered own-body visibility mask and tracks multiple components. The mask uses only ray-visible self geometry; external object IDs/coordinates are not provided to the neural adapter. The same fisheye pixel mapping is applied to RGB and validity. This is an engineered filter, not a biological retinal claim.

Both v3 replays preserve complete physics/gait/world state, all poses and raw RGB exactly. The left cue becomes detectable, peaking24.31Hz in its intended eye. However the left trial's other eye peaks100Hz, including100Hz after removal. The right trial also has post-removal false signals. Thus v3 FAILS specificity and is not promoted. Tests cover masked self expansion, detection of a smaller external expanding component, translation, and track-state restoration.

Raw camera images, validity masks, feature streams, contact sheets and hashes are retained in the replay directories. Next is image-only background-motion compensation and new prospectively registered confounds. Held-out neural evaluation seeds remain unused. Navigation and learning remain unvalidated.

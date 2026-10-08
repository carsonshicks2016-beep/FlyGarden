# Measured leg-response preparation

2026-10-08. **Prepared and tested measurement ingestion; biological comparison not executed.**

The [published study](https://doi.org/10.7554/eLife.60299) reports graded 13B-alpha voltage responses to femur–tibia position. Its electrophysiology and calcium measurements require distinct observation models. These are physiological class observations, not identified BANC roots; all 440 annotated 13B neurons must not inherit the alpha response.

The [Dryad catalog](https://datadryad.org/dataset/doi:10.5061/dryad.k3j9kd55t) was retrieved and pinned: version 94574, CC0, three files with SHA-256 identities. Behavior is 8,951,863 bytes, imaging 804,623 bytes, and electrophysiology 7,496,404,627 bytes. Automated downloads returned HTTP 401/403; no raw physiology files were retrieved. Catalog access does not establish file access or measurement integrity. See [access diagnostic](access-diagnostic.json).

The author's [analysis repository](https://github.com/sagrawal/InterneuronAnalysis/tree/b3c43530d1915c4059cc2046494cf3db1311dbdd) was inspected at the pinned revision. Its ingestion fields include `voltagedata`, `legangles`, `frame_on` and `SampleRate`. A separate reader now preserves the voltage clock and acquired camera exposure clock, converts MATLAB's one-based indices once, and requires verified units, angle convention and junction-correction status. It retains raw voltage and avoids applying a correction twice. It performs no fitting, interpolation to fabricated samples, spike inference or root assignment.

Eight synthetic checks passed for synchronization, correction, invalid indices, missing units and source identity. They establish parser behavior, **not agreement with real physiology**. The original study describes 20 kHz acquisition and a -12 mV junction potential; each actual file still needs verification before those values are applied.

[Measurement requirements](MEASUREMENT_REQUIREMENTS.json) list the remaining dependencies. Next: obtain the public archive through an authorized available download path, inspect actual records and specimen metadata, resolve class correspondence, and register one measured-response comparison before fitting. Missing exact-root correspondence stops an exact-cell claim; a clearly labeled class-level fixture may remain useful.

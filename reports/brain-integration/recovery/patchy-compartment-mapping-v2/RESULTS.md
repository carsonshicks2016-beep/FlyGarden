# Complete site coordinates; opposite-side atlas rejected

The read-only anatomical stage is complete. Every imported pair touching the 34 patchy roots is reconciled to exact released synapse IDs and distinct release/reception coordinates. A bilateral glomerular atlas and a full-network physiological adapter remain unvalidated. The application, brain/controller source, graph, original recordings, and checkpoints are unchanged.

## Exact source/site audit

The complete authors' version-783 archive contains **130,054,535** rows. Its **9,492,998,242-byte** source passes the published MD5 (`f8f1b97c9d4b0ea9b4c8b287f6b99091`) and a retained SHA256. Source identity is rechecked before and after extraction. The archive is already filtered by its authors; "unthresholded" here means no minimum connection-count cutoff, not unfiltered cleft predictions. No additional score threshold, autapse removal, count renormalization, or graph replacement is applied.

All **31,308** modeled pairs and **174,669** anatomical sites reconcile exactly. The prior export lacked **42,645** low-count-pair sites; the complete archive now accounts for those sites. There are **0** deficient and **0** excess modeled pairs. IDs never pass through floating point. Synapse IDs are unique within the selected source subset, and raw source row positions are retained.

The archive additionally contains **87,226** sites on **74,307** pairs absent from the imported controller graph. They remain in the selected-source recording and pair ledger, separately identified. They are not imported into the brain or used to fill missing modeled counts.

Coordinates are native nanometers, per the deposit metadata. Presynaptic release and postsynaptic reception coordinates remain distinct. An input endpoint uses its post position; an output endpoint uses its pre position. Selected-to-selected synapses contribute two directional endpoints but remain one anatomical synapse record. Source neuropil labels are retained independently of glomerular mesh labels.

## Opposite-side registration: failed

The pinned navis/flybrains method uses the FlyWire bounding-box x flip followed by its published non-rigid TPS. All **3,390** source landmarks interpolate with maximum residual **1.06e-08 nm**. All 58 transformed meshes are closed and consistently wound; self-intersections were not separately tested. The existing fixed sensory-anchor reservoir was not used to fit or tune the transform.

For **23,644** opposite-side anchors, **81.06%** are uniquely enclosed, but only **59.89%** of those receive the correct glomerulus label. The prespecified gates were at least 70% unique enclosure and 80% correct labels among uniquely enclosed anchors. The second gate fails. DM1 also fails. Per-glomerulus results and the DM1 confusion table are preserved; no alias, local translation or relabeling is applied to hide the failure.

The published whole-brain registration's availability is not proof of glomerulus-scale accuracy for these atlas boundaries. The mirrored geometry remains a diagnostic artifact and is excluded from candidate/controller assignment.

## Accepted partial anatomy

The validated native-side atlas is applied to the complete modeled sites using their correct directional positions. It produces **179,560** input/output endpoints: **86,045** unique glomerular candidates, **93,513** outside the available atlas, and **2** overlapping/unavailable endpoints. Endpoint totals are not interchangeable with the one-per-synapse site total above. Outside does not mean outside the brain.

Exact-root/model-index candidates and per-direction counts are saved in `anatomical-candidates.json` and `endpoint-root-summary.json`. They are anatomical groupings only: electrical compartments, branch coupling, release units and receptor kinetics remain null. A mesh enclosure or partner label does not establish electrotonic isolation.

## Verification and resources

Eight focused tests pass: exact large IDs, both selected directions, real Arrow chunk boundaries, unmodeled-partner separation, distinct autapse endpoints, nonfinite rejection, native-flip ordering, and published TPS interpolation/batch parity. All **68** per-root input/output totals also match the imported graph exactly. The **4,891** selected-to-selected synapses explain the extra directional endpoints. The two overlapping endpoints remain unavailable and are retained in `overlap-endpoints.csv`. The registration figure has been visually inspected. The unchanged baseline source hashes and the previous delivered v1 artifact hashes are reverified.

The streamed synapse audit took **13.19 s**, with peak RSS **288.7 MiB**. Mirror validation took **23.94 s**; native endpoint mapping took **78.58 s**. These are anatomical analysis timings, not full-brain throughput. The package currently occupies about **17.85 GiB**, including retained verified download ranges and the assembled archive; no recording/checkpoint was removed. Free space is **190.5 GiB**, above the 2-GiB reserve. Reproduction scripts and optional dependency versions are retained.

## Next gate

Obtain independently supported opposite-side glomerular boundaries or prospectively validate a sourced local registration. Then audit exact-root branch topology and specify physiological unit/target conversions before a separate full-network adapter. The prior published DC3/LN2P_c rate fit is not a fit for these DM1/lLN2P_b roots. See `NEXT_REQUIREMENTS.md`.

This stage recovers missing anatomy. It does **not** repair neural persistence, establish useful navigation or learning, or complete Fly Garden.

## Primary sources and reproduction

- [Authors' version-783 synapse deposit](https://doi.org/10.5281/zenodo.10676866), CC BY 4.0, with exact file identity in `archive-identity.json`.
- [Official FlyWire mirroring documentation](https://fafbseg-py.readthedocs.io/en/latest/source/tutorials/flywire_mirror.html); navis revision `cb9a5915b6b3587cb81154f4f77ffc62fe12b03a`, flybrains revision `273333c8d8bf5adeebebd274e554621462e388bd`.
- [Authors' atlas package](https://github.com/natverse/hemibrainr), pinned in the frozen v1 provenance. Mirror source code/package licenses are recorded as GPL-3.0-or-later; no blanket claim about independent data redistribution rights is made.

From the project root, use `.venv-next/bin/python` with `PYTHONPATH=.`. Run `scripts/acquire_unthresholded_783.py`, `scripts/validate_anatomical_mirror.py`, `scripts/audit_unthresholded_783.py`, `scripts/map_verified_783_sites.py`, and `scripts/finish_anatomical_stage_v2.py` in that order. Acquisition reuses verified ranges. The audit worker can wait for verified archive publication automatically. These scripts do not launch a neural simulation or alter application state.

# Patchy-neuron compartment mapping audit

The read-only anatomical audit is complete. A versioned partial mapping is delivered; a full-network graded adapter is not implemented or promoted. All model/controller source hashes remain unchanged.

## What was mapped

All **34** exact version-783 roots (13 lLN2P_a, 12 lLN2P_b, 9 lLN2P_c) join uniquely to annotations and the imported network’s positional neuron ordering. The audit scanned all **15,091,983** aggregated graph rows and all **34,156,320** rows of the downloaded coordinate export. No arbitrary neuron indices or phenotype replacements are used.

For edges touching these roots, the imported graph contains **31,308** aggregate records representing **174,669** anatomical synapses. The coordinate export covers **6,652** records and **132,024** sites, or **75.59%** of those anatomical synapses. Every covered pair matches its imported count exactly. All absent pairs have counts 1–4, accounting for **42,645** missing coordinates. This explains the all-pair parity failure; it is not a count discrepancy among covered pairs. The controller’s low-count connections remain intact.

The downloaded export’s cloud generation, byte count and published MD5 checksum were verified. Decimal root IDs never pass through floating point. Compressed carry-forward columns are decoded across row boundaries; source line numbers are retained with selected sites. The full gzip scan reached EOF and checked its CRC.

## Spatial registration

The pinned authors’ `flywire_al.surf` atlas contains **58** closed, consistently wound glomerular meshes. No coordinate transform, fitted translation, mirror or unverified alias was applied. Mesh units are treated as the source’s native FlyWire-scale coordinates, with alignment tested before use.

A seeded uniform reservoir sampled at most 500 ORN→cognate uniglomerular-PN sites per annotated glomerulus/PN-side group. This provides anatomical registration checks, not physiological or held-out learning validation. Among **23,674** left-PN-side anchors, **95.07%** lie in exactly one mesh; among those uniquely enclosed points, **98.18%** match the annotated glomerulus. The corresponding correct fraction of *all* left samples is **93.34%**. Right-PN-side samples have only **2.06%** unique enclosure. The source atlas is therefore supported for one hemisphere; we have not manufactured a reflected opposite hemisphere. Per-glomerulus failures, sparse samples, absent atlas names and outside points remain visible in `anchor-by-glomerulus.json`.

## Coverage of the selected neurons

| Category | Anatomical synapse sites |
| --- | ---: |
| Uniquely enclosed anatomical candidates | 63,700 |
| Coordinates outside the available atlas | 68,324 |
| Coordinates in overlapping atlas regions | 0 |
| No coordinates in this thresholded export | 42,645 |
| Total imported sites accounted for | 174,669 |

Unique atlas candidates cover **36.47%** of the selected imported site count. “Outside” means outside this available glomerular atlas, not outside the brain; it may include the opposite hemisphere and legitimate non-glomerular sites. Zero observed overlap is specific to this coordinate subset. We keep an explicit overlap policy for other data.

Each exact-root candidate records its model index, input/output counts per enclosed glomerulus and unresolved sites. These are anatomical grouping candidates, not experimentally established electrical compartments. A partner’s ORN/uPN glomerular label remains a separate hint; it never substitutes for a synapse location or automatically labels a local neuron’s whole arbor. Source points do not provide separate release/reception locations; the unthresholded archive schema does.

The three left-side lLN2P_b roots with covered DM1 sites are 720575940637666446 (78 input/36 output), 720575940614429165 (128/103), and 720575940610669614 (202/168). These counts are covered atlas candidates only, not complete DM1 connectivity or fitted inhibitory efficacy. No right-side DM1 assignment is inferred from an annotation or a mirrored drawing.

## Verification and resource use

Five tests passed, covering exact IDs, carry-forward boundaries, atomic malformed-row rejection, ambiguous partner annotations, unavailable overlapping/outside memberships and native mesh containment against known closed boxes. Pair-count and all-count conservation checks pass for the covered subset and the complete imported-count ledger respectively. Four overlapping/outside cases are preserved by the assignment policy.

Graph/coordinate processing took **25.46 seconds**, with peak process RSS **804.9 MiB**. Spatial processing took **76.82 seconds**. These are audit measurements, not full-brain simulation throughput. Optional read-only analysis dependencies and versions are recorded in `provenance.json`. The coverage figure has been visually inspected. Disk space remains above the 2-GiB reserve; no recordings or checkpoints were removed.

## Concrete next requirements

1. Acquire the full unthresholded version-783 synapse table, apply documented filtering, and reconcile each selected pair against the imported graph before assigning the 42,645 missing sites. The public authors’ deposit supplies a 9,492,998,242-byte Feather artifact with separate pre/post positions and cleft scores. Its header/schema was verified; the full file has not yet been downloaded. It must not silently replace the current controller graph or import a different synapse prediction release.
2. Obtain or reproducibly register a glomerular atlas for the opposite hemisphere and test it against that hemisphere’s annotated anchors. A simple geometric reflection is not established by the current evidence. Resolve per-glomerulus alias/split mismatches separately.
3. Review spatial grouping against skeleton branch topology. A glomerular enclosure does not prove electrotonic isolation or a specific coupling coefficient.
4. Specify and validate spike-to-local-activity, graded inhibitory release, receptor target and unit conversions. The published DC3/LN2P_c rate reference is not a fit for these lLN2P_b/DM1 roots. Unknown physiology remains unknown.
5. Only then register a separate full-network adapter protocol, preserve all original topology/counts or explicitly manifest changes, verify checkpoint continuation, and repeat the unchanged recovery/contrast gates before body navigation.

The anatomy audit has progressed from partner-label hints to actual site-level candidates. It has **not** repaired full-brain persistence, validated learning, or completed Fly Garden.

## Primary source links and reproduction

- [FlyWire annotation repository](https://github.com/flyconnectome/flywire_annotations) and [version-783 connectivity deposit](https://doi.org/10.5281/zenodo.10676866).
- [Authors’ glomerular atlas package](https://github.com/natverse/hemibrainr) at the pinned revision and [olfactory connectome study](https://doi.org/10.7554/eLife.66018). Mesh creation/update history is retained in `source/mesh-history.json`.
- [Official synapse retrieval documentation](https://fafbseg-py.readthedocs.io/en/latest/source/generated/fafbseg.flywire.synapses.get_synapses.html). Explicit materialization 783 and source filtering are required; newest/live data are not substitutes for pinned IDs.

From the project root, run `PYTHONPATH=. .venv-next/bin/python scripts/audit_patchy_compartments.py`, then `PYTHONPATH=. .venv-next/bin/python scripts/map_patchy_synapse_sites.py`. These scripts read the local pinned data and write only this diagnostic package. The independent coverage/count finalization and source rechecks are recorded in this package’s receipt. No native brain worker is required.

# Local registration improves labels; bilateral boundary validation remains incomplete

The frozen local correction improves opposite-side anatomical labeling, and an independent exact-root skeleton audit supports the source alignment. **This is not a validated bilateral glomerular atlas or an installed brain repair.** No controller, topology, connection count, neural dynamics, body behavior, recording or checkpoint was changed.

## Candidate and separation of fitting from testing

The candidate translates each published mirrored glomerular mesh to a neuron-balanced calibration center. Shapes, orientations, scales, names and thresholds are not fitted or retuned. Exact ORN root IDs determine a fixed 60% calibration / 40% probe split; all sites belonging to an ORN share its role. The fit uses the median of per-neuron coordinate medians rather than giving high-count connections extra votes. Native postsynaptic positions are in nanometers. Sparse calibration populations and shifts longer than the source mesh diagonal remain unavailable.

The source archive supplies **138,771** cognate ORN→uniglomerular-PN sites; **83,479** are in the fitting group. Parameters for **48** regions were frozen before probe outcomes were read. All **3,174** opposite-side root pairs inspected in the earlier atlas test were excluded from the fresh primary probe. No neuronal root is shared between fitting and that probe. The fit and its source hashes are retained.

The correction is an engineered registration grounded in labeled synapse coordinates. PN soma-side labels and cell-type annotations remain proxies for the intended anatomical population; the test is not independently traced boundary validation or a physiological measurement.

## Primary probe: pooled gate passes, individual coverage is limited

On **2,451** untouched ORN→PN sites from **321** ORNs:

| Same probe cohort | Unique enclosure | Correct labels among enclosed | Correct fraction of all sites |
| --- | ---: | ---: | ---: |
| Published global mirror | 76.58% | 73.95% | 56.63% |
| Frozen local correction | 84.01% | 97.43% | 81.84% |

Neuron-cluster bootstrap 95% intervals are **81.74–85.99%** for unique enclosure and **96.46–98.28%** for label accuracy among enclosed sites. The lower bounds exceed the fixed 70% / 80% gates. The probe is a conservative, selected population of previously uninspected connection pairs, not a representative sample of all brain synapses.

Only nine regions have at least 50 fresh sites and five probe roots and pass their individual point gates: DA1, DA2, DA3, DL3, VA1d, VA1v, VL2a, VM4, VM5d. Those individual checks are descriptive point gates, not per-region bootstrap-certified boundaries. DM1 has no untouched root-pair sample in this primary cohort, so this result does not validate DM1.

## Independent source-class check: coverage confidence fails

A second protocol tested the **same frozen candidate**, with no refitting, on **1,492** cognate ORN→ORN sites in source neuropil AL_R, from **540** presynaptic ORNs. Both endpoints' neurons belong to the original probe group. Autapses are excluded for this validation cohort only; the controller graph remains intact. No fitting ORN or prior source synapse ID is reused. The two probe cohorts can share held-out ORNs: independence here means source-class and synapse-record separation, not independent animals or entirely new neurons. Source AL_R is a coarse anatomical restriction, not a fitted mesh boundary.

| Same independent cohort | Unique enclosure | Correct labels among enclosed | Correct fraction of all sites |
| --- | ---: | ---: | ---: |
| Published global mirror | 80.70% | 55.65% | 44.91% |
| Frozen local correction | 73.12% | 93.13% | 68.10% |

The unique-enclosure 95% interval is **69.57–76.51%**. Its lower bound is below 70%, so the secondary pooled gate **fails**, despite improved label accuracy (**91.08–95.07%** interval). No rounding, threshold relaxation or extra tuning is used to turn this into a pass.

DM1 has 158 sites from 27 presynaptic ORNs. Its corrected unique enclosure is **68.99%**, below the 70% requirement; correct labels among those enclosed reach **97.25%**. This indicates a remaining shape/coverage/overlap problem beyond a simple position error. Outside and multiply enclosed points stay unavailable. Four regions pass secondary individual point gates: DA1, DM3, DM6, DP1l. Only DA1 passes individual point gates in both cohorts. The complete bilateral atlas is not accepted.

## Exact-root branch audit: passes geometric alignment

All **34** patchy neurons have cached full-resolution skeletons matching materialization 783, native nanometer coordinates and their recorded source SHA256. All are single connected trees with zero cycle rank. The audit projects all **179,560** unchanged input/output endpoints onto their exact neuron skeleton segments, preserving source synapse IDs and directional coordinates.

The distance algorithm searches all potentially closer segments using conservative center/radius bounds. It is not a nearest-vertex approximation; tests include a long-segment case where nearest vertex and nearest center give the wrong answer, plus comparison against exhaustive projection.

- Median segment distance: **207.7 nm**.
- 95th / 99th percentiles: **657.5 / 991.4 nm**.
- Within 1 µm: **99.04%**.
- Maximum: **3.95 µm**; zero endpoints beyond 10 µm.

These are geometric alignment measurements, not biological membrane-distance requirements. No distant site is dropped. Segment indices and positions are retained in the sibling `patchy-skeleton-site-audit-v1` package. Branch topology does not establish electrotonic isolation, axial resistance, membrane parameters, local GABA release, or peptide/receptor kinetics. Precomputed skeletons do not supply the required physiological fit.

## Verification, limitations and next gate

Six focused tests pass across the grouped registration and exact segment-search helpers. The secondary audit took **29.41 s**, with peak RSS **740.8 MiB**. The 34-root branch audit took **6.70 s**, with peak RSS **329.7 MiB**. These are analysis timings, not brain throughput. All current sources and frozen prior delivery receipts are reverified. No bulk download or recording/checkpoint deletion was needed.

A report-writing bug shadowed the archive identity with a loop label after the first fit and probe classification finished. The original worker and protocol are preserved. A separate finalizer completed saved statistics without repeating fitting/classification or changing parameters. `report-finalization-amendment.json` records source hashes and that limited repair. The corrected worker remains available for reproduction.

The next anatomical requirement is independently supported opposite-side boundary shape, particularly for DM1, with fresh prospective validation. Do not tune this candidate on these now-inspected probes and call the same data held out. A new candidate needs separate calibration and a genuinely fresh validation source or group. Keep the existing failed global mirror and this partially successful local candidate as distinct lineage records.

After boundary support is adequate, audit branch coupling and spike-to-local-activity/release/target units against the published physiological reference before freezing a separate full-network adapter. The published DC3/LN2P_c fit is still not a fit for the DM1/lLN2P_b pathway. Full-brain recovery/contrast, navigation and learning acceptance remain unpassed.

## Primary source links

- [Authors' version-783 synapse archive](https://doi.org/10.5281/zenodo.10676866), pinned and checksum-verified in the prior coordinate stage.
- [Official FlyWire mirroring documentation](https://fafbseg-py.readthedocs.io/en/latest/source/tutorials/flywire_mirror.html) and the pinned navis/flybrains sources in the previous package.
- [Authors' atlas package](https://github.com/natverse/hemibrainr), pinned in the first spatial audit. This local correction is our engineered method, not a claimed published right-side atlas.
- [Official version-783 skeleton retrieval documentation](https://fafbseg-py.readthedocs.io/en/latest/source/generated/fafbseg.flywire.get_skeletons.html); exact per-root URLs, hashes and local-only license notes are retained in the skeleton audit.

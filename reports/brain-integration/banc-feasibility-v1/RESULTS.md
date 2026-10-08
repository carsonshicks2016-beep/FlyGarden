# Connected nervous-system feasibility assessment

Assessment date: 2026-10-08, America/Chicago. Scope: public-source access, verified annotation inspection, graph metadata, physiology references and a proposed migration design. **No neural simulation, graph import, physiological fitting or controller promotion occurred.**

## Decision in plain language

Keep **BANC as the first anatomy candidate**, with MaleCNS as an independent comparison. BANC gives us candidate sensory cells, brain cells, nerve-cord cells and motor cells in one female specimen. That makes it a better starting point for the user's approved sensory-to-motor goal than attaching another steering formula to the existing brain-only model.

The next problem is making the wiring behave plausibly. A connectome does not supply every cell's electrical properties, receptor effects, muscle mechanics or missing sensory tissue. The same spiking equation for every cell is inadequate as a biological default: published leg-feedback measurements include neurons with graded voltage responses and no detectable action potentials. We should first reproduce a small, measured leg-feedback response, then test that route in the full supported graph. A small fixture is a diagnostic, never a replacement whole-brain qualification.

This assessment supports proceeding to a **versioned import audit and a registered leg-feedback experiment**, not a claim that the nervous system now works. It does not overturn the failed FlyWire direction tests or establish that any particular new mechanism will repair them. The food/predator garden remains the destination; walking precedes flight.

## What was actually accessed

All selected static sources were accessible without an account or token. The downloaded annotation files total **124,999,591 bytes (119.21 MiB)**. Their lengths and checksums match their source receipts. Cached tables were independently rehashed before analysis. Graphs were inspected through exact HTTP byte ranges: **827,776 bytes** of footer/batch metadata plus **24,576 bytes** of schemas. No connection values, synapse archives or morphology bundles were downloaded.

| Source | Pinned identity for this assessment | License / boundary |
|---|---|---|
| BANC | Dataverse DOI `10.7910/DVN/7WTH1N`, released catalog 3.0, v888 metadata file 14033740, metrics 14034271; exact lengths, MD5 and SHA-256 in `source-access.json` | CC BY 4.0. Materialization, detector version and annotation revision are separate identities. |
| BANC reference graph | Archived simple-v2 file 13992792; simple-v3 file 13918810. Probed GCS object lengths/MD5 ETags match those archived catalog entries. | Full payload checksums and edge contents still need verification on import. |
| MaleCNS | Static `v1.0` annotation and transmitter tables; generation, ETag, MD5 and SHA-256 receipts retained | Official downloads state CC BY. NeuPrint API authentication is separate from public static access. |
| BANC analysis code | `htem/BANC-project` revision `e31a2e26b9937dca72e5ca1c1960df6454d76114` | Assessment reference; not imported into production. |
| Physiological references | Publication/DOI and repository revisions recorded in `primary-references.json`; steering catalog retained separately | Raw experiment payloads were not downloaded or fitted. |

Primary access documentation: [BANC archive](https://doi.org/10.7910/DVN/7WTH1N), [BANC analysis source](https://github.com/htem/BANC-project/tree/e31a2e26b9937dca72e5ca1c1960df6454d76114), [MaleCNS downloads](https://male-cns.janelia.org/download/).

Attribution: BANC anatomy/annotations are credited to Bates, Phelps, Kim, Yang and collaborators; MaleCNS anatomy/annotations to the collaborators named by the FlyEM/Janelia project. The selected annotation extracts retain their upstream CC BY attribution through these dataset links, source hashes and dataset namespaces. Application/assessment code retains the repository's own license; it does not relicense upstream data.

**Important revision trap:** the live GCS `banc_888_meta.feather` is 57,503,026 bytes; the archived file is 57,550,610 bytes, with a different checksum. The shared `v888` label does not make them interchangeable. This inventory uses the archived table. Mixing live annotations with archived graph assumptions requires a new explicit version comparison.

## Annotation inventory and exact identity checks

These are **rows in imported annotation artifacts**, not accepted modeled-neuron counts. Missing classifications, fragments, non-neural cells and proofreading flags must be resolved explicitly before constructing a neuron population. The metrics and archived metadata have identical BANC primary-ID sets.

| Measured inventory | BANC archived v888 | MaleCNS v1.0 |
|---|---:|---:|
| Annotation rows | 188,508 | 211,577 |
| Annotation columns | 81 | 36 |
| Primary identifier | `banc_888_id`, exact string | `bodyId`, exact integer serialized as string |
| Central / optic / VNC intrinsic annotations | 31,879 / 72,947 / 12,866 | 32,164 / 89,403 / 13,161 |
| Descending / ascending annotations | 1,316 / 1,849 | 1,314 / 1,846 |
| Motor annotations | 805 | 815 (708 VNC + 107 central-brain motor) |
| Missing broad class | 28,632 | 44,877 |

BANC additionally contains 12,750 glial, 162 tracheal and 195 `not_a_neuron` rows. **11,344 unclassified rows are marked proofread TRUE.** A proofread-only filter is therefore neither a neuronal-membership definition nor a complete functional-class inventory.

The generic BANC `root_id` differs from `banc_888_id` in **16,319 rows**. Two `root_888` entries also disagree with the release key: `720575941229247158` and `720575940434812394`. Both are unproofread, status `TOO_SMALL`; their inclusion remains unresolved. Use the documented release key, retain the discrepancy, and never repair it by guessed index or floating-point conversion.

`selected-identities.json` lists exact candidate roots and their available side, QC and transmitter fields. It is an inspection roster, not a functioning adapter. Matched cell types across specimens establish possible correspondence, not identity or portable neural state.

### Relevant candidate populations

| Exact annotation or population | BANC count | MaleCNS count | Practical use / limitation |
|---|---:|---:|---|
| `ORN_DM1` | 90 (45 left, 45 right) | 74 | Candidate odor channel; receptor/odor physiology must be matched. |
| `ORN_DM2` | 60 (35 left, 25 right) | 54 | Unequal counts are retained, not silently balanced. |
| `DM1_lPN` | 2 | 2 | Bilateral projection-neuron diagnostic; subtraction is not a motor circuit. |
| `DNp09`, `DNa02`, `DNa01`, `DNg13` | 2 of each | 2 of each | Candidate walking/steering-route cells; exact dynamics and downstream delivery still untested. |
| `LPLC2`, `LC4`, `DNp01` | 181 / 114 / 2 | 185 / 126 / 2 | Candidate visual/escape routes; annotations do not prove complete retinal input or the correct behavioral context. |
| `MBON01`, `MBON11`, `MBON32` | 2 of each | 2 of each | Learning-route candidates; BANC's two `MBON01` rows are both annotated left. |
| `PAM01`, `PPL101` | 38 / 2 | 44 / 2 | Candidate reinforcement cells; transmitter identity is not a complete learning rule. |

**Do not invent a right MBON01:** the archived side annotations are ambiguous for bilateral use. This blocks that particular bilateral mapping pending morphology/curation review; it does not prove the biological right cell is absent. Two cells with the same type name are not enough to qualify a left/right pair.

The BANC leg inventory is especially useful for a first embodied diagnostic:

- 391 leg motor rows: front 139, middle 126, hind 126. Front-leg motor annotations include named flexor/extensor and other muscle targets, but activation-to-force and body-actuator correspondence are not supplied by this table.
- Front-leg chordotonal groups: claw 52, hook 53, club 106. These counts include sensory and sensory-ascending annotations. `front-leg-identities.json` retains those 211 exact roots plus the 139 front-leg motor roots.
- Across BANC: 2,131 chordotonal-class rows, including 25 sensory-ascending rows; primary sensory annotations additionally include 201 campaniform and 320 hair-plate rows. A body's generic contact sensor cannot be relabeled as all these organs.
- Wing and haltere motor annotations exist (64 and 27). Their presence is anatomical evidence, not a working flight controller.

Route continuity, connection counts along these routes, muscle mapping and morphology alignment remain **unverified** because graph values and skeletons were not imported in this phase.

## What the convenient graph files do and do not contain

| Probed artifact | Serialized rows | Compressed bytes | Actual schema |
|---|---:|---:|---|
| BANC simple v2 | 11,752,828 | 305,250,378 | string `pre`, string `post`, int32 `count`, double `norm`, int32 `post_count`, int32 `pre_count` |
| BANC simple v3 | 13,620,865 | 359,161,658 | Same |
| MaleCNS full weights v1 | 151,856,684 | 1,051,241,946 | int64 `body_pre`, `body_post`, `weight` |

These counts come from serialized Arrow batch metadata, validated against independent PyArrow decoding on generated multi-batch fixtures. They are **not** endpoint-validated modeled pairs, and they are **not anatomical synapse-site totals**. No site total was calculated in this assessment.

MaleCNS's full weights table includes all segments with synapses, not only curated neurons. Its 151.9 million rows cannot be compared directly with a qualified neuronal graph. The transmitter table has 1,835,518 unique body rows; 187,016 join to the annotation table, 24,561 annotation rows lack a transmitter-table match, and 1,648,502 transmitter rows lie outside that annotation table. Those extra segments must not become millions of invented neurons.

BANC's simple table is an analysis convenience. The authored dataset documentation states that **autapses are excluded at build time**. The pinned analysis loader separately applies a proofread/roughly-proofread endpoint filter. Its plotting/influence thresholds are not instructions for a full-model import. See [authored dataset documentation](https://github.com/sjcabs/fly_connectome_data_tutorial/blob/85c66244cfb2c02b2442905c4428b42a0d8e6656/data/dataset_documentation/banc_data.md) and [pinned graph loader](https://github.com/htem/BANC-project/blob/e31a2e26b9937dca72e5ca1c1960df6454d76114/R/startup/banc-edgelist.R).

Start with v2 for a source-replication audit. Treat v3 as a separate detector revision, not an automatic upgrade. Before calling an import the full supported graph, inspect the site archive or another verified complete representation, recover supported self-connections, and reconcile every endpoint, exclusion and site count. If that cannot be done, label the imported graph's omissions explicitly. Do not apply a new pair-count threshold.

## Physiological gaps and useful response measurements

### Transmitter labels are not synaptic effects

In archived BANC, 34,455 rows lack a predicted transmitter and 123,022 lack a verified label. Of 64,483 rows with both labels, 4,889 predictions are absent from the comma-separated verified set. This is a descriptive disagreement count, not a classifier accuracy benchmark: verification and cross-dataset curation have their own provenance.

Neither inspected dataset provides universal postsynaptic receptor identities, membrane constants, adaptation parameters, synaptic conductances, short-term dynamics or neuromuscular force laws. MaleCNS's sparse `receptorType` field is not a universal postsynaptic receptor atlas. A transmitter prediction alone does not establish excitation, inhibition or neuromodulation for every target. In particular, do not carry the old model's blanket glutamate sign or dopamine-as-fast-current assumptions into BANC without an explicit physiological basis. Preserve co-transmitter labels and unresolved effects.

### Published validation candidates

| Measurement | Source / access checked | What it can discriminate | What remains unresolved |
|---|---|---|---|
| Leg position, movement and vibration tuning | [Mamiya et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6481666/); [Agrawal et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7752136/) | Sensory transduction versus downstream dynamics; graded versus spiking responses; reflex sign and context | Physiological driver/filled-cell identities still need exact BANC correspondence. 13B lineage membership alone is insufficient. |
| Proprioceptive voltage/calcium/behavior recordings | [Dryad DOI 10.5061/dryad.k3j9kd55t](https://datadryad.org/dataset/doi:10.5061/dryad.k3j9kd55t) | A concrete route toward reproducing measured response curves | Catalog has behavior 8.95 MB, imaging 804.62 KB and electrophysiology 7.50 GB; raw files have not been imported or parsed. |
| DNa01/DNa02 steering activity and walking behavior | [Rayshubskiy et al., eLife 102230](https://elifesciences.org/articles/102230); [Dataverse DOI 10.7910/DVN/0NCLP1](https://doi.org/10.7910/DVN/0NCLP1) | Native steering measurements instead of assuming odor-PN subtraction drives action | Catalog 1.2, CC0, 380 files, 157.89 GB total. Select relevant sessions; no bulk physiological download occurred. Cell, stimulus, speed and measurement modality must match. |
| ORN temporal gain and recovery | [Gorur-Shandilya et al., eLife 27670](https://pmc.ncbi.nlm.nih.gov/articles/PMC5524537/) | Receptor transduction versus spike-generation adaptation | Published receptor/odor combinations must match individually; ab3A is not the current DM1 receptor population. No exact-root fit exists. |
| Visual flash, moving-edge and flow responses | [Lappalainen et al. 2024](https://www.nature.com/articles/s41586-024-07939-3), [official Flyvis implementation](https://github.com/TuragaLab/flyvis/tree/92b3845cc426dd309a1a0e1b3890156c42e14021) | A graded visual-model reference and held-out response tests | Its task-trained model is a comparison or explicit composite module, not an exact BANC optic-lobe checkpoint. |

The published 13B-alpha recordings show graded voltage responses without detectable spikes. That is a strong reason to support heterogeneous cell models. It is **not** evidence that all 440 BANC `13B` hemilineage rows are those recorded cells, or that adaptation caused every previous failed result.

### Missing vision and peripheral tissue

The BANC source reports absent lamina, R1–R6 photoreceptors, ocelli and ocellar ganglion, with incomplete branches for affected classes. The specimen also has documented damage regions. Importing its surviving optic cells cannot restore missing tissue. See [BANC publication](https://www.nature.com/articles/s41586-026-10735-w) and the archived `banc_problem_regions.csv` receipt.

A future eye-image pathway needs explicit optics, receptor/lamina response models and a documented interface into the reconstructed tissue. Any cross-specimen or fitted replacement is a **composite reconstruction**, with its own source, mapping and validation. An absent exact `R1` annotation is not, by itself, the evidence for absent tissue; the specimen report is. Skeleton units, matching and alignment still require their own sample audit.

## Resources: measurements versus estimates

Verified hardware: ARM Mac, 16 GiB physical RAM, 12 physical/logical CPU cores. Source-access collection took 530.30 seconds, mostly many serial HTTP metadata requests. Local cache verification/inventory took 4.07 seconds, peak process RSS **1.273 GiB**. These are annotation-tool measurements, not application or neural benchmarks. Free space at the source receipt was 194.72 GiB; the 2 GiB reserve was preserved.

Illustrative storage floors below assume two int32 dense endpoint indices and one float64 weight per serialized record. They exclude source-ID maps, import copies, solver state, sparse indexing, delays, queues, receptor classes, additional synaptic state, neurons, physics, viewer and checkpoints.

| Artifact | Illustrative 16-byte/row floor | Each additional float64 per edge |
|---|---:|---:|
| BANC v2 simple | 179.33 MiB | 89.67 MiB |
| BANC v3 simple | 207.84 MiB | 103.92 MiB |
| MaleCNS all-segment weights | 2.263 GiB | 1.131 GiB |

This does **not** prove BANC fits under 10 GiB or MaleCNS does not. The BANC floor omits autapses/other unsupported endpoints; MaleCNS membership filtering has not occurred. A full mixed-dynamics model could have much larger overhead. BANC's archived v2 enriched site file is 17,146,564,854 bytes on disk; streaming aggregation and a disk plan are necessary if it is used to recover complete connectivity. No such archive was downloaded.

For context only, the existing FlyWire point-model diagnostic reported peak RSS 2.493 GiB and roughly 0.11 simulated seconds per wall second in [its measured results](../recovery/sensory-context-capability-v1/RESULTS.md). Those numbers cannot be extrapolated into a BANC runtime, particularly with graded cells and muscle feedback. Benchmark one new worker before enabling concurrency. Preserve slow, synchronized simulation and recorded playback.

## Ranked risks and next decision

1. **Highest scientific risk: physiological underdetermination.** Uniform neuron/synapse defaults do not reproduce all relevant known cell behavior. Test a measured response before another large tuning sweep. The contribution to old failures is not causally isolated by this assessment.
2. **High implementation risk: source identity and graph membership.** Mutable `v888` metadata, generic-ID divergence, self-connection omissions and all-segment MaleCNS rows are concrete observed import hazards. Fixing importer mistakes is distinct from choosing new physiological assumptions.
3. **High embodiment risk: missing sensory tissue and muscle mechanics.** Full anatomical CNS data still needs organ/body adapters, verified coordinate units, force/activation models and feedback. The current supplied walking controller remains a comparison while these are developed.
4. **High validation risk: substituting a convenient readout for a native route.** A neural-only preference score, symmetry assumption or colorful viewer can obscure an unqualified motor mechanism. Validate source-to-recipient delivery, then real body effects, with matched interventions.
5. **Operational uncertainty: full mixed-model memory and throughput.** Raw graph size alone is insufficient. A single-worker, exact-source benchmark is required before long experiments.

The proposed order and implementation boundaries are in [MIGRATION_DESIGN_V1.md](MIGRATION_DESIGN_V1.md). The initial discriminating checks are in [NEXT_EXPERIMENTS.md](NEXT_EXPERIMENTS.md). Both are proposals, not executed scientific protocols.

## Reproduction and verification

From the FlyGarden checkout, with the existing Python 3.12 environment:

```sh
.venv-next/bin/python scripts/assess_cns_feasibility.py --report reports/brain-integration/banc-feasibility-recheck --cache data/anatomy-feasibility-recheck
.venv-next/bin/python scripts/inventory_cns_annotations.py --report reports/brain-integration/banc-feasibility-recheck --cache data/anatomy-feasibility-recheck --fetch-schemas
.venv-next/bin/python -m pytest tests/test_cns_feasibility.py -q
```

Use fresh output paths to preserve this receipt; the collector now refuses to overwrite a finalized receipt. The original collector used for this receipt is retained in `source-snapshot/assess_cns_feasibility.py`, matching the receipt's source hash; the added overwrite guard leaves its collection logic unchanged. The access script queries the current released catalog: if it changes, retain a **new assessment**, do not call it exact reproduction of these files. Exact reproduction uses the recorded archive file IDs/checksums and MaleCNS object identities; the inventory refuses caches that disagree with its receipt. Network/catalog failure is not evidence that anatomy is missing.

Eleven focused tests pass: independent Arrow row-count fixtures; exact large IDs and duplicate/float rejection; categorical missing annotations; sensory-ascending leg membership; strict ranged access; low-disk refusal; interrupted-download preservation; mismatched-cache preservation; and refusal to overwrite finalized receipts. Independent column checks confirm the 350-row leg roster; 28 local links resolve, and 160 protected source/goals/ledger/historical-report files match the pre-assessment commit. See `verification.json`. The scripts never instantiate Brian2 or body physics.

Published evidence consists of these bounded reports, receipts, inventory and selected identity rosters. Full downloaded tables remain in the ignored local cache `data/anatomy-feasibility-v1`. Previous failed reports, controllers, model state and all 39 acceptance requirements retain their prior status. This assessment creates no new scientific pass.

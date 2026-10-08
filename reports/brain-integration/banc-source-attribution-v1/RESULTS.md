# BANC anatomical import and source attribution

2026-10-08. **Source consistency established; physiology and native neural control remain unqualified.**

The raw and simplified archived sources passed complete size/MD5 checks. Local SHA-256 receipts are retained. All **218,460,853 raw records** parsed with unique synapse IDs and no invalid declared fields. At the unchanged v2 size threshold of 5, **197,100,067 sites** form **153,209,879 ordered segmentation pairs**. No pair-count cutoff was applied; smaller sites and original fields remain in the raw archive.

## Source contracts

| Check | Result |
|---|---|
| Original no-self projection A | FAILED: 156,311 differing pairs; 0 shared-count mismatches |
| Closed annotation graph, self included (B) | 11,752,828 pairs / 35,733,096 sites; 0 mismatches |
| Independent raw reread | 218,460,853 rows; 1,972 selected pairs / 10,398 sites across 408 roots; 0 mismatches |

The original no-self expectation came from documentation and inspected processing code. Independent inspection of the original Feather disproved it: this archive includes **156,311 equal-endpoint pairs / 1,422,866 sites**, with positive counts, unique pairs and nonzero endpoints. The file is not corrupt or duplicated. Current upstream code is an inspected reference, not a verified build revision for this archive.

This follow-up was registered after that observation and explicitly corrects a **source assumption**. It is not a neural bug fix, a relaxed behavioral criterion or a retrospective pass of v1. Projection A and the failed execution remain preserved. Projection B uses identical membership and size rules, retains self-connections, and requires exact equality of every ordered pair/count. All match. [Protocols and full results](results.json) retain this distinction.

An independent PyArrow reader scanned the entire raw gzip/CSV again and exactly reproduced the selected counts. The roster includes named sensory/descending candidates and front-leg sensory/motor cells. [Exact route counts](selected-route-counts.json) preserve string IDs. This validates static connections, not a physiological pathway or behavior.

## Coverage and claim boundaries

The release has 188,508 annotation rows; membership partitions are:

| Membership | Rows |
|---|---:|
| annotated_neuron_candidate | 146,769 |
| conflict | 2 |
| excluded_non_neural | 13,107 |
| unclassified | 28,630 |

Eligible endpoints include **100,543,110 distinct IDs outside annotations** and 176,813 inside. Outside IDs are unclassified segmentation objects, not 100,543,110 extra neurons. Which are fragments, artifacts or other structures requires evidence. The raw archive and grouped outside index are retained rather than silently omitted or turned into neural units.

**161,366,971 eligible raw sites (81.9%) have at least one endpoint outside the annotation set.** This explains the difference between raw site totals and the closed annotated graph. Annotation rows include non-neural and unresolved classes; neither count is a qualified modeled-neuron population. All eligible sites reconcile exactly across the explicit partitions in [results.json](results.json).

Equal-endpoint records include 6 zero/unassigned sites and 2,510,638 nonzero equal-ID sites. Equal segmentation IDs do not establish biological autapses. No self-edge weight or neural sign is assigned here.

## Resources and interruptions

Sources occupy **11.70 GiB** and imported Parquet artifacts **4.48 GiB**, alongside small difference files and reports. Original normalization took about 5.9 monotonic minutes. The first job recorded 29.3 monotonic minutes including downloads before stopping on the source assumption. Host sleep or clock changes can make calendar elapsed differ.

The first worker's sampled RSS reached 2.31 GiB; its whole-run peak was not captured on failure. The completed follow-up measured peak RSS **1.03 GiB** and took **3.0 monotonic minutes**, excluding source rehashing before worker creation. One Python worker used a 2 GB DuckDB memory setting; library I/O can use background threads. The engine setting is not a total-process memory guarantee. The 2 GiB disk reserve was preserved.

The first follow-up's unrestricted endpoint union exceeded its memory limit and stopped safely. An execution-only amendment counts the existing grouped outside index plus an annotation-restricted union, producing the same exact metric with bounded memory. Its failed execution is retained. Source identities, thresholds, membership and scientific criteria are unchanged. Original v1 operational amendments cover printing, immutable completed-run handling/memory allocation and stricter restart provenance.

Forty-two focused checks passed across strict import, exact IDs, self/zero/non-neural handling, checksum/range failures, interruption/resume, immutable evidence, protocol provenance, dual source contracts and measurement timing. No neural simulation or controller fit was launched.

## Next

Resolve supported neuronal membership, self-edge quality and physiological correspondence before building electrical dynamics. [Leg-measurement preparation](../leg-physiology-preparation-v1/RESULTS.md) has synthetic clock/unit checks, but automated Dryad downloads failed and no raw-data fit exists. Hemilineage 13B does not identify 13B-alpha. Retrieve actual measurements and establish class-level or exact-root correspondence before registering the first response-model comparison.

The existing FlyWire controller, failures, checkpoints and all 39 acceptance qualifications are unchanged. This is data integrity and accounting; it does not establish an organic digital animal, walking, flight or learning.

Sources: [BANC archive, CC BY 4.0](https://doi.org/10.7910/DVN/7WTH1N), [inspected processing source](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1), [authored documentation](https://github.com/sjcabs/fly_connectome_data_tutorial/blob/85c66244cfb2c02b2442905c4428b42a0d8e6656/data/dataset_documentation/banc_data.md).

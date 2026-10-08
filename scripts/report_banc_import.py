"""Publish the preserved import failure and registered source attribution."""
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cns_audit.banc import ROOT,CACHE
from cns_audit.download import atomic_json,hashes


def publish(path,text):
    if path.exists(): raise FileExistsError(f'Preserve finalized report: {path}')
    temp=path.with_name(path.name+'.tmp');temp.write_text(text);temp.rename(path)


def main():
    origin=ROOT/'reports/brain-integration/banc-import-v1'
    follow=ROOT/'reports/brain-integration/banc-source-attribution-v1'
    result=json.loads((follow/'results.json').read_text())
    boundaries=json.loads((origin/'boundary-count-diagnostic.json').read_text())
    sources=json.loads((origin/'source-receipts.json').read_text())
    a,b=result['comparisons']['A'],result['comparisons']['B']
    raw=result['raw'];check=result['independent_routes'];ends=result['endpoint_counts'];closed=boundaries['raw_both_annotated']
    outside_sites=raw['eligible_sites']-closed['sites']
    source_bytes=sum(s['bytes'] for s in sources.values())
    imported_bytes=sum(p.stat().st_size for p in (CACHE/'imported').glob('*.parquet'))
    text=f'''# BANC anatomical import and source attribution

2026-10-08. **Source consistency established; physiology and native neural control remain unqualified.**

The raw and simplified archived sources passed complete size/MD5 checks. Local SHA-256 receipts are retained. All **{raw['rows']:,} raw records** parsed with unique synapse IDs and no invalid declared fields. At the unchanged v2 size threshold of 5, **{raw['eligible_sites']:,} sites** form **{boundaries['raw_all']['pairs']:,} ordered segmentation pairs**. No pair-count cutoff was applied; smaller sites and original fields remain in the raw archive.

## Source contracts

| Check | Result |
|---|---|
| Original no-self projection A | FAILED: {a['different_pairs']:,} differing pairs; {a['shared_count_mismatch']:,} shared-count mismatches |
| Closed annotation graph, self included (B) | {closed['pairs']:,} pairs / {closed['sites']:,} sites; {b['different_pairs']} mismatches |
| Independent raw reread | {check['raw_rows']:,} rows; {check['pairs']:,} selected pairs / {check['sites']:,} sites across {check['selected_roots']} roots; {check['mismatch_pairs']} mismatches |

The original no-self expectation came from documentation and inspected processing code. Independent inspection of the original Feather disproved it: this archive includes **156,311 equal-endpoint pairs / 1,422,866 sites**, with positive counts, unique pairs and nonzero endpoints. The file is not corrupt or duplicated. Current upstream code is an inspected reference, not a verified build revision for this archive.

This follow-up was registered after that observation and explicitly corrects a **source assumption**. It is not a neural bug fix, a relaxed behavioral criterion or a retrospective pass of v1. Projection A and the failed execution remain preserved. Projection B uses identical membership and size rules, retains self-connections, and requires exact equality of every ordered pair/count. All match. [Protocols and full results](results.json) retain this distinction.

An independent PyArrow reader scanned the entire raw gzip/CSV again and exactly reproduced the selected counts. The roster includes named sensory/descending candidates and front-leg sensory/motor cells. [Exact route counts](selected-route-counts.json) preserve string IDs. This validates static connections, not a physiological pathway or behavior.

## Coverage and claim boundaries

The release has 188,508 annotation rows; membership partitions are:

| Membership | Rows |
|---|---:|
'''
    text+='\n'.join(f'| {k} | {v:,} |' for k,v in result['membership_counts'].items())
    text+=f'''

Eligible endpoints include **{ends['outside_annotation_ids']:,} distinct IDs outside annotations** and {ends['in_annotation_set']:,} inside. Outside IDs are unclassified segmentation objects, not {ends['outside_annotation_ids']:,} extra neurons. Which are fragments, artifacts or other structures requires evidence. The raw archive and grouped outside index are retained rather than silently omitted or turned into neural units.

**{outside_sites:,} eligible raw sites ({outside_sites/raw['eligible_sites']:.1%}) have at least one endpoint outside the annotation set.** This explains the difference between raw site totals and the closed annotated graph. Annotation rows include non-neural and unresolved classes; neither count is a qualified modeled-neuron population. All eligible sites reconcile exactly across the explicit partitions in [results.json](results.json).

Equal-endpoint records include {boundaries['raw_zero_equal']['sites']:,} zero/unassigned sites and {boundaries['raw_nonzero_equal']['sites']:,} nonzero equal-ID sites. Equal segmentation IDs do not establish biological autapses. No self-edge weight or neural sign is assigned here.

## Resources and interruptions

Sources occupy **{source_bytes/2**30:.2f} GiB** and imported Parquet artifacts **{imported_bytes/2**30:.2f} GiB**, alongside small difference files and reports. Original normalization took about 5.9 monotonic minutes. The first job recorded 29.3 monotonic minutes including downloads before stopping on the source assumption. Host sleep or clock changes can make calendar elapsed differ.

The first worker's sampled RSS reached 2.31 GiB; its whole-run peak was not captured on failure. The completed follow-up measured peak RSS **{result['resources']['peak_process_rss_bytes']/2**30:.2f} GiB** and took **{result['resources']['monotonic_followup_seconds']/60:.1f} monotonic minutes**, excluding source rehashing before worker creation. One Python worker used a 2 GB DuckDB memory setting; library I/O can use background threads. The engine setting is not a total-process memory guarantee. The 2 GiB disk reserve was preserved.

The first follow-up's unrestricted endpoint union exceeded its memory limit and stopped safely. An execution-only amendment counts the existing grouped outside index plus an annotation-restricted union, producing the same exact metric with bounded memory. Its failed execution is retained. Source identities, thresholds, membership and scientific criteria are unchanged. Original v1 operational amendments cover printing, immutable completed-run handling/memory allocation and stricter restart provenance.

Forty-two focused checks passed across strict import, exact IDs, self/zero/non-neural handling, checksum/range failures, interruption/resume, immutable evidence, protocol provenance, dual source contracts and measurement timing. No neural simulation or controller fit was launched.

## Next

Resolve supported neuronal membership, self-edge quality and physiological correspondence before building electrical dynamics. [Leg-measurement preparation](../leg-physiology-preparation-v1/RESULTS.md) has synthetic clock/unit checks, but automated Dryad downloads failed and no raw-data fit exists. Hemilineage 13B does not identify 13B-alpha. Retrieve actual measurements and establish class-level or exact-root correspondence before registering the first response-model comparison.

The existing FlyWire controller, failures, checkpoints and all 39 acceptance qualifications are unchanged. This is data integrity and accounting; it does not establish an organic digital animal, walking, flight or learning.

Sources: [BANC archive, CC BY 4.0](https://doi.org/10.7910/DVN/7WTH1N), [inspected processing source](https://github.com/htem/bancpipeline/tree/5c333c12f0b9e03873f88cf4e23cad34c0bb49c1), [authored documentation](https://github.com/sjcabs/fly_connectome_data_tutorial/blob/85c66244cfb2c02b2442905c4428b42a0d8e6656/data/dataset_documentation/banc_data.md).
'''
    publish(follow/'RESULTS.md',text)
    publish(origin/'RESULTS.md','''# BANC import v1: preserved source-assumption failure

2026-10-08. Both sources passed full checksum checks. All 218,460,853 raw records parsed with unique synapse IDs and valid declared numeric fields. Raw-site, eligible-pair, membership and outside-endpoint artifacts are retained.

**The registered no-self expectation for the simplified table failed.** Independent reading of the original Feather found 156,311 equal-endpoint pairs / 1,422,866 sites. Counts are positive, endpoints nonzero and pairs unique. The data are not corrupt or duplicated; the documentation-based source assumption was wrong for this archive.

The original protocol, interruption and registered source snapshot remain preserved. Three execution-only amendments do not change this gate or any neural acceptance criterion.

A separately registered source-attribution check verifies both the original projection and the actual inclusive archive. See [its results](../banc-source-attribution-v1/RESULTS.md). Do not call original v1 passing. The live controller, checkpoints and all 39 acceptance qualifications are unchanged.

[Source receipts](source-receipts.json), [raw integrity](raw-integrity.json), [independent original-table diagnostic](simple-table-diagnostic.json), [protocol](protocol.json), [restart tutorial](TUTORIAL.md).
''')
    atomic_json(follow/'report-identity.json',dict(results_sha256=hashes(follow/'results.json')['sha256'],report_sha256=hashes(follow/'RESULTS.md')['sha256'],generator_sha256=hashes(ROOT/'scripts/report_banc_import.py')['sha256']))
    print(follow/'RESULTS.md')


if __name__=='__main__':main()

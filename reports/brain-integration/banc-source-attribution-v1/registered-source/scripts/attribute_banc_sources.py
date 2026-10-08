"""Registered follow-up to a contradicted archived-table self-edge assumption.

Preserves the v1 failed gate. Checks both contracts without changing thresholds,
membership, neuron signs, or any scientific behavior acceptance criterion.
"""
import argparse
import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cns_audit import banc as b
from cns_audit.download import atomic_json,hashes,RESERVE

ROOT=b.ROOT
ORIGIN=b.REPORT
REPORT=ROOT/'reports/brain-integration/banc-source-attribution-v1'
OUTPUT=ROOT/'data/banc-source-attribution-v1'


def source_code():
    paths=['scripts/attribute_banc_sources.py','cns_audit/banc.py','cns_audit/download.py']
    return {p:hashes(ROOT/p)['sha256'] for p in paths}


def register():
    if (REPORT/'protocol.json').exists(): raise FileExistsError('Registered follow-up already exists')
    prior=json.loads((ORIGIN/'protocol.json').read_text())
    artifact_names=['membership','eligible-pairs','simple-comparison']
    receipts={}
    for name in artifact_names:
        path=b.CACHE/'imported'/f'{name}.parquet'
        receipt=json.loads(path.with_suffix('.receipt.json').read_text())
        if hashes(path)!=receipt['identity'] or receipt['protocol_sha256']!=hashes(ORIGIN/'protocol.json')['sha256']:
            raise ValueError('Origin artifact provenance mismatch')
        receipts[name]=receipt
    protocol=dict(schema_version=1,registered_at=b.utc(),purpose='Source-contract attribution, not neural simulation',
        revealed_before_registration='Original simplified Feather independently contains 156311 equal-endpoint records. Original no-self expectation failed.',
        original_protocol_sha256=hashes(ORIGIN/'protocol.json')['sha256'],
        original_failed_check_preserved=True,origin_artifacts=receipts,
        sources=json.loads((ORIGIN/'source-receipts.json').read_text()),
        comparisons=dict(A='Original: size>=5 raw pairs; both release-key endpoints annotated; exclude self',
                         B='Actual archived contract candidate: identical size and membership, retain self'),
        acceptance=dict(B='All ordered pairs and counts exactly equal archive, including self; report failure otherwise',
                        independent='Second raw gzip CSV reader exactly reproduces all selected pairs and total raw row count',
                        A='Report differences unchanged; never relabel original no-self gate as passing'),
        independent_check=prior['independent_check'],
        stop_rules=['Hash/protocol/source drift','Invalid/duplicate pairs','Disk reserve','Independent-reader mismatch'],
        code_sha256=source_code(),resources=dict(workers=1,threads=1,memory_limit='2GB',reserve_bytes=RESERVE),
        classification='Explicit correction of a source assumption; not a neural bug fix or relaxed behavioral gate',
        weights_assigned=False,controller_promoted=False,acceptance_39_unchanged=True)
    atomic_json(REPORT/'protocol.json',protocol)
    atomic_json(REPORT/'protocol-identity.json',hashes(REPORT/'protocol.json'))
    print('Registered source attribution',hashes(REPORT/'protocol.json')['sha256'])


def run():
    if (REPORT/'results.json').exists(): raise FileExistsError('Follow-up finalized; preserve evidence')
    path=REPORT/'protocol.json'; protocol=json.loads(path.read_text())
    if hashes(path)!=json.loads((REPORT/'protocol-identity.json').read_text()) or source_code()!=protocol['code_sha256']:
        raise ValueError('Follow-up identity drift')
    if hashes(ORIGIN/'protocol.json')['sha256']!=protocol['original_protocol_sha256']:
        raise ValueError('Origin protocol drift')
    for name,receipt in protocol['origin_artifacts'].items():
        if hashes(b.CACHE/'imported'/f'{name}.parquet')!=receipt['identity']:
            raise ValueError('Origin artifact drift')
    for name,receipt in protocol['sources'].items():
        observed=hashes(b.CACHE/name)
        if any(observed[k]!=receipt[k] for k in ['bytes','sha256','md5']): raise ValueError('Raw/comparison source drift')
    original_report=b.REPORT; b.REPORT=REPORT
    audit=b.Audit(protocol)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    audit.output=OUTPUT
    try:
        for view,name in [('membership','membership'),('pairs','eligible-pairs'),('simple','simple-comparison')]:
            audit.view(view,b.CACHE/'imported'/f'{name}.parquet')
        con=audit.con
        validity=con.execute('SELECT count(*),count(DISTINCT (pre,post)),count(*) FILTER(WHERE pre IS NULL OR post IS NULL OR count IS NULL OR pre=0 OR post=0 OR count<=0) FROM simple').fetchone()
        if validity[0]!=validity[1] or validity[2]: raise ValueError('Invalid simplified records')
        con.execute('CREATE VIEW annotated_raw AS SELECT p.* FROM pairs p JOIN membership a ON a.root=p.pre JOIN membership b ON b.root=p.post')
        results={}
        for variant,where in [('A','WHERE pre<>post'),('B','')]:
            audit.progress('source_comparison',variant=variant)
            query=('SELECT coalesce(r.pre,s.pre) AS pre,coalesce(r.post,s.post) AS post,r.count AS raw_count,s.count AS simple_count '
                   f'FROM (SELECT * FROM annotated_raw {where}) r FULL JOIN simple s USING(pre,post) WHERE r.count IS DISTINCT FROM s.count')
            diff=audit.publish_parquet(f'differences-{variant}.parquet',query)
            audit.view('diff',diff)
            fields=['different_pairs','raw_only','simple_only','shared_count_mismatch']
            counts=con.execute('SELECT count(*),count(*) FILTER(WHERE simple_count IS NULL),count(*) FILTER(WHERE raw_count IS NULL),count(*) FILTER(WHERE raw_count IS NOT NULL AND simple_count IS NOT NULL) FROM diff').fetchone()
            results[variant]=dict(zip(fields,counts)) | {'exact_match':counts[0]==0}
        independent=audit.independent_routes()
        origin_raw=json.loads((ORIGIN/'raw-integrity.json').read_text())
        if independent['raw_rows']!=origin_raw['rows'] or not independent['exact_match']:
            raise ValueError('Independent raw-source mismatch')
        audit.progress('membership_and_boundary_counts')
        boundary=con.execute("SELECT coalesce(a.membership,'outside_annotations'),coalesce(b.membership,'outside_annotations'),count(*),sum(p.count)::UBIGINT "
            'FROM pairs p LEFT JOIN membership a ON a.root=p.pre LEFT JOIN membership b ON b.root=p.post GROUP BY 1,2 ORDER BY 1,2').fetchall()
        partitions=[dict(pre=a,post=b,pairs=c,sites=d) for a,b,c,d in boundary]
        if sum(p['sites'] for p in partitions)!=origin_raw['eligible_sites']:
            raise ValueError('Unaccounted eligible sites')
        self_records=con.execute("SELECT coalesce(m.membership,'outside_annotations'),count(*),sum(p.count)::UBIGINT FROM pairs p LEFT JOIN membership m ON m.root=p.pre WHERE p.pre=p.post GROUP BY 1 ORDER BY 1").fetchall()
        membership=con.execute('SELECT membership,count(*) FROM membership GROUP BY 1 ORDER BY 1').fetchall()
        counts=con.execute('WITH e AS (SELECT pre AS root FROM pairs UNION SELECT post AS root FROM pairs) SELECT count(*),count(*) FILTER(WHERE root=0),count(*) FILTER(WHERE m.root IS NOT NULL) FROM e LEFT JOIN membership m USING(root)').fetchone()
        result=dict(completed_at=b.utc(),original_v1_no_self_gate='FAILED, preserved',comparisons=results,
            raw=origin_raw,independent_routes=independent,membership_counts=dict(membership),partitions=partitions,
            endpoint_counts=dict(raw_endpoint_ids=counts[0],zero_ids=counts[1],in_annotation_set=counts[2]),
            equal_endpoint_records=[dict(membership=a,pairs=c,sites=d) for a,c,d in self_records],
            qualification='Source consistency only; biological neuron membership/dynamics remain unresolved',
            source_consistency_passed=results['B']['exact_match'],model_ready=False,
            resources=dict(monotonic_followup_seconds=time.monotonic()-audit.started,
                peak_process_rss_bytes=max(audit.peak_rss,resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)),
            dataset_license='CC BY 4.0',new_neural_simulations=0,acceptance_39_unchanged=True)
        atomic_json(REPORT/'results.json',result)
        audit.progress('complete',source_consistency_passed=result['source_consistency_passed'],model_ready=False)
        print(json.dumps(result,indent=2))
    except BaseException as exc:
        atomic_json(REPORT/f'interruption-{time.time_ns()}.json',dict(at=b.utc(),error=f'{type(exc).__name__}: {exc}',evidence_preserved=True))
        raise
    finally:
        audit.stop.set();audit.guard.join(timeout=2);audit.con.close();b.REPORT=original_report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['register','run'])
    args=parser.parse_args()
    register() if args.action=='register' else run()

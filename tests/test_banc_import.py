"""End-to-end tiny fixtures: exact roots, autapses, exclusions and failures."""
import gzip
import json

import pyarrow as pa
import pyarrow.feather as feather
import pytest

from cns_audit import banc as b
from cns_audit.download import hashes


@pytest.fixture
def fixture(monkeypatch, tmp_path):
    duckdb = b.duckdb_module()
    monkeypatch.setattr(b, 'duckdb_module', lambda: duckdb)
    cache, report = tmp_path/'data', tmp_path/'report'
    cache.mkdir(); report.mkdir()
    monkeypatch.setattr(b, 'ROOT', tmp_path)
    monkeypatch.setattr(b, 'CACHE', cache)
    monkeypatch.setattr(b, 'REPORT', report)
    meta, metrics = cache/'meta.feather', cache/'metrics.feather'
    monkeypatch.setattr(b, 'META', meta); monkeypatch.setattr(b, 'METRICS', metrics)
    a, z, glia = '720575941633499884','720575941472733451','720575941662395704'
    feather.write_feather(pa.table({'banc_888_id':[a,z,glia], 'root_888':[a,z,glia],
        'super_class':['sensory','motor','glia']}), meta)
    feather.write_feather(pa.table({'banc_888_id':[a,z,glia]}), metrics)
    roster = tmp_path/'reports/brain-integration/banc-feasibility-v1'
    roster.mkdir(parents=True)
    (roster/'roster.json').write_text(json.dumps({'rows':[{'banc_888_id':a},{'banc_888_id':z}]}))
    (report/'protocol.json').write_text('{}')
    sources = [dict(name='raw.csv.gz'),dict(name='simple.feather')]
    monkeypatch.setattr(b, 'SOURCES', sources)
    rows = [(1,a,z,5),(2,a,z,10),(3,a,a,5),(4,a,z,4),(5,z,a,5),
            (6,'0',a,5),(7,glia,a,5),(8,'720575940000000001',a,5)]
    def write_rows(data=rows):
        with gzip.open(cache/'raw.csv.gz','wt') as out:
            for id,pre,post,size in data:
                out.write(','.join(map(str,[id]+[1]*9+[size,'77195682137926786',pre,'77195682137926786',post]))+'\n')
        feather.write_feather(pa.table({'pre':[a,z,glia], 'post':[z,a,a], 'count':[2,1,1]}), cache/'simple.feather')
        for source in sources:
            source.update(hashes(cache/source['name']),url='https://example.invalid')
    write_rows()
    protocol = {'independent_check':{'rosters':{'roster.json':'unused'}}}
    return protocol, rows, write_rows, report, cache


def test_full_tiny_audit_accounts_self_zero_glia_and_preserves_first_row(fixture):
    protocol, _, _, report, _ = fixture
    result = b.Audit(protocol).run()
    assert result['raw']['rows'] == 8
    assert result['raw']['eligible_sites'] == 7
    assert result['raw']['eligible_self_sites'] == 1
    assert result['raw']['eligible_pairs'] == 6
    assert result['simple_comparison']['exact_match']
    assert result['independent_routes']['selected_roots'] == 2
    assert result['independent_routes']['sites'] == 4
    assert result['independent_routes']['pairs'] == 3
    assert result['passed_integrity'] and not result['model_ready']
    assert any(p['pre']=='outside_annotations' for p in result['partitions'])
    assert any(p['pre']=='excluded_non_neural' for p in result['partitions'])
    finalized = {p.name:p.read_bytes() for p in report.iterdir() if p.is_file()}
    with pytest.raises(FileExistsError, match='finalized'):
        b.Audit(protocol).run()
    assert finalized == {p.name:p.read_bytes() for p in report.iterdir() if p.is_file()}


def test_duplicate_id_blocks_qualification_without_discarding(fixture):
    protocol, rows, write, report, cache = fixture
    write(rows + [rows[0]])
    with pytest.raises(ValueError, match='duplicate raw'):
        b.Audit(protocol).run()
    stats = json.loads((report/'raw-integrity.json').read_text())
    assert stats['rows']==9 and stats['unique_synapse_ids']==8
    assert not (report/'audit-results.json').exists()
    assert (cache/'imported/raw-sites.parquet').exists()


@pytest.mark.parametrize('bad_size', [-1, 'NaN', 'inf'])
def test_invalid_size_blocks_qualification(fixture, bad_size):
    protocol, rows, write, _, _ = fixture
    write(rows + [(9,rows[0][1],rows[0][2],bad_size)])
    with pytest.raises(ValueError, match='Invalid'):
        b.Audit(protocol).run()


def test_simple_difference_reported_without_retuning(fixture):
    protocol, _, _, _, cache = fixture
    feather.write_feather(pa.table({'pre':['720575941633499884'], 'post':['720575941472733451'], 'count':[99]}),cache/'simple.feather')
    b.SOURCES[1].update(hashes(cache/'simple.feather'))
    result = b.Audit(protocol).run()
    diff = result['simple_comparison']
    assert diff['different_pairs']==3 and diff['shared_count_mismatch']==1
    assert not diff['exact_match'] and not diff['filters_changed_to_fit']


def test_conflicted_and_unclassified_membership_remain_separate():
    table = pa.table({'banc_888_id':['12','11','13'], 'root_888':['99','11','13'],
                      'super_class':['sensory',None,'trachea']})
    result = b.membership(table).to_pylist()
    assert [r['root'] for r in result]==[11,12,13]
    assert [r['membership'] for r in result]==['unclassified','conflict','excluded_non_neural']
    with pytest.raises(ValueError,match='release ID'):
        b.membership(pa.table({'banc_888_id':['12','12'],'root_888':['12','12'],'super_class':['sensory','motor']}))


def test_stage_resume_requires_protocol_identity_not_only_file_hash(fixture):
    protocol,_,_,_,cache=fixture
    audit=b.Audit(protocol)
    try:
        path=audit.publish_parquet('fixture.parquet','SELECT 1 AS value')
        assert audit.publish_parquet('fixture.parquet','SELECT 1 AS value')==path
        receipt=path.with_suffix('.receipt.json')
        data=json.loads(receipt.read_text()); data['protocol_sha256']='wrong protocol'
        receipt.write_text(json.dumps(data))
        with pytest.raises(ValueError,match='receipt'): audit.publish_parquet('fixture.parquet','SELECT 1 AS value')
    finally:
        audit.stop.set(); audit.guard.join(timeout=2); audit.con.close()

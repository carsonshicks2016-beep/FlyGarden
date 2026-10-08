"""The source-contract diagnostic must preserve the original failed gate."""
import json

import pyarrow as pa
import pyarrow.feather as feather
import pytest

from tests.test_banc_import import fixture
from cns_audit import banc as b
from cns_audit.download import hashes
from scripts import attribute_banc_sources as follow


def test_self_contract_attribution_preserves_failed_original(fixture,monkeypatch):
    protocol,rows,_,origin,cache=fixture
    protocol['independent_check']['rosters']['roster.json']=hashes(b.ROOT/'reports/brain-integration/banc-feasibility-v1/roster.json')['sha256']
    (origin/'protocol.json').write_text(json.dumps(protocol))
    a,z,g='720575941633499884','720575941472733451','720575941662395704'
    feather.write_feather(pa.table({'pre':[a,z,g,a],'post':[z,a,a,a],'count':[2,1,1,1]}),cache/'simple.feather')
    b.SOURCES[1].update(hashes(cache/'simple.feather'))
    with pytest.raises(ValueError,match='simplified'): b.Audit(protocol).run()
    original_failed={p.name:p.read_bytes() for p in origin.iterdir() if p.is_file()}
    output=origin.parent/'follow-report'
    monkeypatch.setattr(follow,'ORIGIN',origin);monkeypatch.setattr(follow,'REPORT',output)
    monkeypatch.setattr(follow,'OUTPUT',cache/'follow-output')
    follow.register(); follow.run()
    result=json.loads((output/'results.json').read_text())
    assert result['comparisons']['A']['different_pairs']==1
    assert not result['comparisons']['A']['exact_match']
    assert result['comparisons']['B']['exact_match']
    assert result['independent_routes']['exact_match']
    assert result['source_consistency_passed'] and not result['model_ready']
    assert result['original_v1_no_self_gate']=='FAILED, preserved'
    expected={int(root) for _,pre,post,size in rows if size>=5 for root in [pre,post]}
    assert result['endpoint_counts']['raw_endpoint_ids']==len(expected)==5
    assert result['endpoint_counts']['outside_annotation_ids']==2
    assert result['endpoint_counts']['in_annotation_set']==3
    assert result['endpoint_counts']['zero_ids']==1
    assert original_failed=={p.name:p.read_bytes() for p in origin.iterdir() if p.is_file()}
    with pytest.raises(FileExistsError): follow.run()

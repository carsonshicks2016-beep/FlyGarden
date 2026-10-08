"""Protocol freezing, source drift and explicit execution-only amendments."""
import json

import pytest

from cns_audit import banc as b
from cns_audit.download import atomic_json, hashes


def test_registration_confirmation_and_protocol_immutable(tmp_path,monkeypatch,capsys):
    monkeypatch.setattr(b,'REPORT',tmp_path)
    protocol=b.register()
    confirmation=json.loads(capsys.readouterr().out)
    assert confirmation['sha256']==hashes(tmp_path/'protocol.json')['sha256']
    assert b.load_protocol()==protocol
    with pytest.raises(FileExistsError): b.register()
    assert b.load_protocol()==protocol


def test_source_drift_requires_explicit_chained_amendment(tmp_path,monkeypatch):
    monkeypatch.setattr(b,'REPORT',tmp_path)
    protocol=b.register()
    changed=protocol['code_sha256'] | {'cns_audit/banc.py':'a'*64}
    monkeypatch.setattr(b,'code_identities',lambda:changed)
    with pytest.raises(ValueError,match='source drift'): b.load_protocol()
    atomic_json(tmp_path/'execution-amendment-001.json',dict(protocol_sha256=hashes(tmp_path/'protocol.json')['sha256'],prior_code_sha256=protocol['code_sha256'],code_sha256=changed))
    assert b.load_protocol()==protocol
    amend=json.loads((tmp_path/'execution-amendment-001.json').read_text())
    amend['prior_code_sha256']={}
    atomic_json(tmp_path/'execution-amendment-001.json',amend)
    with pytest.raises(ValueError,match='chain'): b.load_protocol()


def test_protocol_edit_stops_resume(tmp_path,monkeypatch):
    monkeypatch.setattr(b,'REPORT',tmp_path)
    b.register()
    path=tmp_path/'protocol.json'
    path.write_text(path.read_text()+' ')
    with pytest.raises(ValueError,match='protocol drift'): b.load_protocol()

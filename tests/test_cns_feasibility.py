"""Scientific-count and data-integrity checks; no network or neural simulation."""
import io
from types import SimpleNamespace

import pandas as pd
import pyarrow as pa
import pytest

from scripts import assess_cns_feasibility as access
from scripts import inventory_cns_annotations as inventory


@pytest.mark.parametrize("rows,batch_size", [(0, 3), (13, 3), (100, 23)])
def test_metadata_only_arrow_count_matches_independent_reader(monkeypatch, rows, batch_size):
    table = pa.table({"pre": [str(720575941554922119 + i) for i in range(rows)],
                      "post": ["720575941540370069"] * rows, "count": list(range(rows))})
    sink = pa.BufferOutputStream()
    with pa.ipc.new_file(sink, table.schema, options=pa.ipc.IpcWriteOptions(compression="lz4")) as writer:
        for batch in table.to_batches(max_chunksize=batch_size):
            writer.write_batch(batch)
    raw = sink.getvalue().to_pybytes()
    requests = []

    def read(info, start, length):
        requests.append((start, length))
        return raw[start:start + length]

    monkeypatch.setattr(access, "range_get", read)
    result = access.arrow_graph_metadata({"bytes": len(raw)})
    independently_decoded = pa.ipc.open_file(pa.BufferReader(raw)).read_all()
    assert result["record_rows"] == independently_decoded.num_rows == rows
    assert result["batches"] == pa.ipc.open_file(pa.BufferReader(raw)).num_record_batches
    assert result["range_bytes_read"] == sum(length for _, length in requests)


def test_exact_ids_preserve_large_integers_and_reject_corruption():
    values = pd.Series([720575941554922119, 720575941540370069], dtype="int64")
    assert inventory.exact_ids(values).tolist() == ["720575941554922119", "720575941540370069"]
    for bad in (values.astype(float), pd.Series(["12", "12"]), pd.Series(["1.2"]), pd.Series([None])):
        with pytest.raises(ValueError):
            inventory.exact_ids(bad)


def test_missing_categorical_annotation_is_counted():
    result = inventory.counts(pd.Series(pd.Categorical(["Traced", None, "Traced"])))
    assert result == {"Traced": 2, "<missing>": 1}


def test_leg_roster_includes_sensory_ascending_without_inventing_labels():
    frame = pd.DataFrame({
        "super_class": ["sensory", "sensory_ascending", "motor", "sensory", "sensory"],
        "body_part_effector": [None, None, "front_leg", None, None],
        "cell_class": ["chordotonal_organ_neuron", "chordotonal_organ_neuron", "motor_neuron", "chordotonal_organ_neuron", "bristle_neuron"],
        "cell_sub_class": ["front_leg_claw_chordotonal_organ_neuron", "front_leg_club_chordotonal_organ_neuron", None,
                           "hind_leg_claw_chordotonal_organ_neuron", "front_leg_briste_neuron"]})
    assert inventory.front_leg_mask(frame).tolist() == [True, True, True, False, False]


class Response(io.BytesIO):
    def __init__(self, body, status=206, headers=None):
        super().__init__(body)
        self.status, self.headers = status, headers or {}


def test_range_rejects_full_response_and_inconsistent_identity(monkeypatch):
    info = {"url": "https://example.invalid/graph", "bytes": 100, "etag": '"pinned"'}
    observed = []

    def full_response(url, method="GET", extra=None):
        observed.append(extra)
        return Response(b"x" * 100, status=200)

    monkeypatch.setattr(access, "request", full_response)
    with pytest.raises(ValueError, match="exact byte range"):
        access.range_get(info, 5, 4)
    assert observed == [{"Range": "bytes=5-8", "If-Match": '"pinned"'}]
    monkeypatch.setattr(access, "request", lambda *a, **kw: Response(b"xxxx", headers={"Content-Range": "bytes 6-9/100"}))
    with pytest.raises(ValueError):
        access.range_get(info, 5, 4)


def test_low_disk_stops_before_request(monkeypatch, tmp_path):
    monkeypatch.setattr(access.shutil, "disk_usage", lambda path: SimpleNamespace(free=access.RESERVE + 3))
    monkeypatch.setattr(access, "request", lambda *a, **kw: pytest.fail("No request at disk reserve"))
    with pytest.raises(OSError, match="reserve"):
        access.fetch_metadata("https://example.invalid", tmp_path / "table", 4)
    assert not list(tmp_path.iterdir())


def test_incomplete_download_preserves_partial_without_publishing(monkeypatch, tmp_path):
    monkeypatch.setattr(access, "request", lambda *a, **kw: Response(b"abc"))
    with pytest.raises(ValueError, match="identity mismatch"):
        access.fetch_metadata("https://example.invalid", tmp_path / "table", 4)
    assert not (tmp_path / "table").exists()
    parts = list(tmp_path.glob("table.*.part"))
    assert len(parts) == 1 and parts[0].read_bytes() == b"abc"


def test_existing_mismatched_cache_is_preserved(monkeypatch, tmp_path):
    cached = tmp_path / "table"
    cached.write_bytes(b"abc")
    monkeypatch.setattr(access, "request", lambda *a, **kw: pytest.fail("Must not replace mismatched cache"))
    with pytest.raises(ValueError, match="identity differs"):
        access.fetch_metadata("https://example.invalid", cached, 4)
    assert cached.read_bytes() == b"abc"


def test_finalized_receipt_refuses_overwrite_before_network(monkeypatch, tmp_path):
    report = tmp_path / "report"
    report.mkdir()
    receipt = report / "source-access.json"
    receipt.write_text('{"preserved":true}')
    monkeypatch.setattr("sys.argv", ["assess", "--report", str(report)])
    monkeypatch.setattr(access, "json_get", lambda *a: pytest.fail("Must stop before fetching another catalog"))
    with pytest.raises(FileExistsError, match="preserve evidence"):
        access.main()
    assert receipt.read_text() == '{"preserved":true}'

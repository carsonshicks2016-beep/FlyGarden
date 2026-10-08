"""Read-only CNS source/annotation assessment; never constructs a neural model.

Downloads only selected annotation tables and small catalogs. Graphs are probed
with bounded HTTP byte ranges, never loaded or imported into the application.
Keeps cached source bytes and interrupted downloads, and enforces the disk reserve.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import struct
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pyarrow.feather as feather

ROOT = Path(__file__).resolve().parents[1]
RESERVE = 2 * 2**30
DATAVERSE = "https://dataverse.harvard.edu/api"
PERSISTENT_ID = "doi:10.7910/DVN/7WTH1N"
MALE_BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/"
BANC_BASE = "https://storage.googleapis.com/lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/banc_888/"
HEADERS = {"User-Agent": "FlyGarden read-only anatomy feasibility assessment"}


def digest(path: Path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2) + "\n")
    temp.replace(path)


def request(url, method="GET", extra=None):
    return urllib.request.urlopen(
        urllib.request.Request(url, method=method, headers=HEADERS | (extra or {})),
        timeout=30,
    )


def json_get(url):
    with request(url) as response:
        content = response.read(4 * 2**20 + 1)
        if len(content) > 4 * 2**20:
            raise ValueError("Catalog exceeds this assessment's request budget")
        return json.loads(content)


def head(url):
    with request(url, "HEAD") as response:
        headers = response.headers
        return {"url": url, "resolved_url": response.url, "status": response.status,
                "bytes": int(headers.get("Content-Length", 0)),
                "etag": headers.get("ETag"), "generation": headers.get("x-goog-generation"),
                "modified": headers.get("Last-Modified"), "hash": headers.get("x-goog-hash"),
                "accept_ranges": headers.get("Accept-Ranges")}


def fetch_metadata(url, path, expected_bytes, expected_md5=None, etag=None):
    if expected_bytes > 64 * 2**20:
        raise ValueError("Only annotation-sized files are allowed in this assessment")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.stat().st_size != expected_bytes or (expected_md5 and digest(path, "md5") != expected_md5):
            raise ValueError(f"Existing cache identity differs: {path}")
        return {"cached": True, "bytes": expected_bytes, "sha256": digest(path), "md5": digest(path, "md5")}
    if shutil.disk_usage(path.parent).free - expected_bytes < RESERVE:
        raise OSError("Paused before download: preserving 2 GiB disk reserve")
    # Earlier interrupted bytes are preserved; every attempt gets a fresh file.
    partial = path.with_name(path.name + f".{time.time_ns()}.part")
    start = time.monotonic()
    received = 0
    with request(url, extra={"If-Match": etag} if etag else None) as response, partial.open("xb") as output:
        for block in iter(lambda: response.read(2**20), b""):
            if received + len(block) > expected_bytes:
                raise ValueError("Response exceeds registered annotation size")
            if shutil.disk_usage(path.parent).free - len(block) < RESERVE:
                raise OSError("Download paused cleanly at disk reserve; partial preserved")
            output.write(block)
            received += len(block)
    if received != expected_bytes or (expected_md5 and digest(partial, "md5") != expected_md5):
        raise ValueError(f"Downloaded source identity mismatch; bytes retained: {partial}")
    partial.rename(path)
    return {"cached": False, "bytes": received, "sha256": digest(path), "md5": digest(path, "md5"),
            "download_seconds": time.monotonic() - start}


def range_get(info, start, length):
    if length < 1 or length > 2**20:
        raise ValueError("Byte-range request must be between 1 byte and 1 MiB")
    headers = {"Range": f"bytes={start}-{start + length - 1}"}
    if info.get("etag"):
        headers["If-Match"] = info["etag"]
    with request(info["url"], extra=headers) as response:
        content = response.read(length + 1)
        expected = f"bytes {start}-{start + length - 1}/{info['bytes']}"
        if response.status != 206 or response.headers.get("Content-Range") != expected or len(content) != length:
            raise ValueError("Server did not honor exact byte range; no bulk read attempted")
        return content


def field(buf, table, slot):
    """Locate a FlatBuffers field, including an absent optional scalar."""
    vtable = table - struct.unpack_from("<i", buf, table)[0]
    size = struct.unpack_from("<H", buf, vtable)[0]
    entry = 4 + 2 * slot
    if entry >= size:
        return None
    offset = struct.unpack_from("<H", buf, vtable + entry)[0]
    return table + offset if offset else None


def dereference(buf, position):
    return position + struct.unpack_from("<I", buf, position)[0]


def arrow_graph_metadata(info):
    """Read Arrow footer and each batch metadata only; no edge bodies fetched."""
    if range_get(info, 0, 6) != b"ARROW1":
        raise ValueError("Expected an Arrow IPC file")
    tail = range_get(info, info["bytes"] - 10, 10)
    if tail[4:] != b"ARROW1":
        raise ValueError("Invalid Arrow footer")
    footer_size = struct.unpack_from("<I", tail)[0]
    footer = range_get(info, info["bytes"] - 10 - footer_size, footer_size)
    table = struct.unpack_from("<I", footer)[0]
    position = field(footer, table, 3)  # Footer.recordBatches: vector<Block>
    vector = dereference(footer, position)
    batches = struct.unpack_from("<I", footer, vector)[0]
    rows, transferred = 0, 16 + len(footer)
    messages = hashlib.sha256(footer)
    for index in range(batches):
        offset, metadata_bytes, body_bytes = struct.unpack_from("<qi4xq", footer, vector + 4 + index * 24)
        metadata = range_get(info, offset, metadata_bytes)
        transferred += len(metadata)
        messages.update(metadata)
        first = struct.unpack_from("<I", metadata)[0]
        prefix = 8 if first == 0xFFFFFFFF else 4
        message = prefix + struct.unpack_from("<I", metadata, prefix)[0]
        header_type = field(metadata, message, 1)
        if metadata[header_type] != 3:  # MessageHeader.RecordBatch
            raise ValueError("Expected record batch header")
        batch = dereference(metadata, field(metadata, message, 2))
        row_field = field(metadata, batch, 0)
        count = struct.unpack_from("<q", metadata, row_field)[0] if row_field is not None else 0
        if count < 0 or body_bytes < 0:
            raise ValueError("Invalid batch size")
        rows += count
    return {"record_rows": rows, "batches": batches, "source_bytes": info["bytes"],
            "range_bytes_read": transferred, "footer_and_batch_metadata_sha256": messages.hexdigest(),
            "scope": "Serialized row count only; no connectivity values or endpoint validity inspected"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "reports/brain-integration/banc-feasibility-v1")
    parser.add_argument("--cache", type=Path, default=ROOT / "data/anatomy-feasibility-v1")
    args = parser.parse_args()
    if (args.report / "source-access.json").exists():
        raise FileExistsError("Finalized source receipt already exists; choose a new --report path to preserve evidence")
    args.report.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    url = DATAVERSE + "/datasets/:persistentId/?persistentId=" + urllib.parse.quote(PERSISTENT_ID)
    catalog = json_get(url)
    version = catalog["data"]["latestVersion"]
    write_json(args.cache / "banc-dataverse-catalog.json", catalog)
    files = {item["dataFile"]["filename"]: item["dataFile"] for item in version["files"]}
    result = {"schema_version": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Read-only data/annotation inspection; zero neural simulations or production migration",
              "source_script_sha256": digest(Path(__file__)), "banc_catalog": {
                  "url": url, "dataset_doi": PERSISTENT_ID, "version": f"{version['versionNumber']}.{version['versionMinorNumber']}",
                  "state": version["versionState"], "license": version.get("license"),
                  "sha256": digest(args.cache / "banc-dataverse-catalog.json")},
              "assets": {}, "graph_probes": {}, "errors": []}
    # Dataverse filenames/MD5s identify the static release independently of the mutable GCS object.
    for name in ("banc_888_meta.feather", "banc_888_metrics.feather", "banc_problem_regions.csv"):
        item = files[name]
        url = DATAVERSE + f"/access/datafile/{item['id']}"
        artifact = {"source": "BANC archived Dataverse", "url": url, "catalog_file_id": item["id"],
                    "expected_bytes": item["filesize"], "catalog_checksum": item["checksum"]}
        print("Inspecting", name, flush=True)
        artifact.update(fetch_metadata(url, args.cache / name, item["filesize"], item["checksum"]["value"]))
        result["assets"][name] = artifact
    for name in ("body-annotations-male-cns-v1.0-minconf-0.5.feather", "body-neurotransmitters-male-cns-v1.0.feather"):
        info = head(MALE_BASE + name)
        hashes = dict(x.split("=", 1) for x in (info["hash"] or "").split(",") if "=" in x)
        expected_md5 = base64.b64decode(hashes["md5"]).hex() if "md5" in hashes else (info["etag"] or "").strip('"')
        print("Inspecting", name, flush=True)
        info.update(fetch_metadata(info["url"], args.cache / name, info["bytes"], expected_md5, info["etag"]))
        result["assets"][name] = info
    # Record live/static divergence without replacing the archived metadata.
    live = head(BANC_BASE + "banc_888_meta.feather")
    result["banc_live_metadata"] = live | {"same_size_as_archived": live["bytes"] == files["banc_888_meta.feather"]["filesize"],
                                           "same_md5_as_archived": (live["etag"] or "").strip('"') == files["banc_888_meta.feather"]["checksum"]["value"]}
    for key, url in (("banc_v2", BANC_BASE + "banc_888_edgelist_simple_v2.feather"),
                     ("banc_v3", BANC_BASE + "banc_888_edgelist_simple_v3.feather"),
                     ("male_v1", MALE_BASE + "connectome-weights-male-cns-v1.0-minconf-0.5.feather")):
        print("Probing graph metadata", key, flush=True)
        info = head(url)
        if key.startswith("banc"):
            item = files[url.rsplit("/", 1)[-1]]
            info["matches_archived_md5"] = (info["etag"] or "").strip('"') == item["checksum"]["value"]
            info["archived_bytes"] = item["filesize"]
            info["archived_file_id"] = item["id"]
            if not info["matches_archived_md5"]:
                raise ValueError("Graph live/archive divergence requires an explicit alternate probe")
        try:
            result["graph_probes"][key] = info | arrow_graph_metadata(info)
        except Exception as exc:
            result["graph_probes"][key] = info | {"error": f"{type(exc).__name__}: {exc}"}
            result["errors"].append({"graph": key, "error": str(exc)})
    result["runtime_seconds"] = time.monotonic() - start
    result["free_disk_gib_after"] = shutil.disk_usage(args.cache).free / 2**30
    result["reserve_gib"] = RESERVE / 2**30
    result["downloaded_annotation_bytes"] = sum(x["bytes"] for x in result["assets"].values())
    write_json(args.report / "source-access.json", result)
    print("Completed source access assessment; no simulation constructed", flush=True)


if __name__ == "__main__":
    main()

"""Inspect verified annotation caches, without importing a neural graph or model.

Counts are annotation rows, not a qualified modeled neuron population. Exact IDs
are serialized as strings; cell types and cross-specimen matches never imply
identity. Use --fetch-schemas only for bounded remote Arrow schema inspection.
"""
from __future__ import annotations

import argparse
import json
import re
import resource
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather

try:
    from .assess_cns_feasibility import ROOT, digest, range_get, write_json
except ImportError:  # Direct script invocation.
    from assess_cns_feasibility import ROOT, digest, range_get, write_json

TARGETS = ("ORN_DM1", "ORN_DM2", "DM1_lPN", "DNp09", "DNa02", "DNa01", "DNg13",
           "DNp01", "LC4", "LPLC2", "MBON01", "MBON11", "MBON32", "PAM01", "PPL101",
           "L1", "R1", "R7")
INSPECT_TYPES = set(TARGETS) - {"L1", "R1", "R7", "LC4", "LPLC2", "ORN_DM1", "ORN_DM2"}
FRONT_LEG_CHORDOTONAL_TYPES = {
    f"front_leg_{kind}_chordotonal_organ_neuron" for kind in ("claw", "hook", "club")
}


def counts(series):
    # Dictionary-encoded MaleCNS columns must be cast before adding a missing label.
    return {str(k): int(v) for k, v in series.astype(object).fillna("<missing>").value_counts().items()}


def exact_ids(series):
    if series.isna().any():
        raise ValueError("Primary ID contains missing values")
    if pd.api.types.is_float_dtype(series.dtype):
        raise ValueError("Floating-point IDs are forbidden")
    values = series.astype(str)
    if not values.map(lambda x: bool(re.fullmatch(r"[1-9][0-9]*", x))).all():
        raise ValueError("Primary IDs must be exact positive integer strings")
    if values.duplicated().any():
        raise ValueError("Primary ID is not unique")
    return values


def records(frame, columns):
    # JSON roundtrip turns categorical values, NaNs and numpy scalars into plain data.
    return json.loads(frame.loc[:, columns].to_json(orient="records"))


def front_leg_mask(frame):
    return ((frame.super_class.eq("motor") & frame.body_part_effector.eq("front_leg")) |
            (frame.super_class.isin(["sensory", "sensory_ascending"]) &
             frame.cell_class.eq("chordotonal_organ_neuron") &
             frame.cell_sub_class.isin(FRONT_LEG_CHORDOTONAL_TYPES)))


def verified_frame(cache, receipt, name):
    path = cache / name
    identity = receipt["assets"][name]
    if path.stat().st_size != identity["bytes"] or digest(path) != identity["sha256"]:
        raise ValueError(f"Source receipt mismatch: {name}")
    table = feather.read_table(path)
    return table.to_pandas(), {"rows": table.num_rows, "columns": table.num_columns,
                               "decoded_arrow_bytes": table.nbytes, "schema": str(table.schema),
                               "sha256": identity["sha256"]}


def inventory_banc(frame, metrics):
    frame = frame.copy()
    frame["banc_888_id"] = exact_ids(frame["banc_888_id"])
    metrics_ids = exact_ids(metrics["banc_888_id"])
    result = {"primary_key": "banc_888_id", "counts_are": "Annotation rows; not accepted modeled neurons",
              "metrics_id_set_equal": set(metrics_ids) == set(frame.banc_888_id),
              "class_counts": counts(frame.super_class), "region_counts": counts(frame.region),
              "proofread_counts": counts(frame.proofread), "flow_counts": counts(frame.flow),
              "cell_function_counts": counts(frame.cell_function),
              "generic_root_mismatches": int(frame.root_id.ne(frame.banc_888_id).sum()),
              "root_888_conflicts": records(frame.loc[frame.root_888.ne(frame.banc_888_id)],
                                            ["banc_888_id", "root_id", "root_888", "cell_type", "side", "proofread", "status"]),
              "unclassified_proofread_true": int((frame.super_class.isna() & frame.proofread.eq("TRUE")).sum()),
              "targets": {}, "bilateral_ambiguities": []}
    for cell_type in TARGETS:
        target = frame.loc[frame.cell_type.eq(cell_type)]
        result["targets"][cell_type] = {"rows": len(target), "sides": counts(target.side)}
        if len(target) == 2 and set(target.side.dropna()) != {"left", "right"}:
            result["bilateral_ambiguities"].append(cell_type)
    sensory = frame.loc[frame.super_class.eq("sensory")]
    motor = frame.loc[frame.super_class.eq("motor")]
    result["sensory_class_counts"] = counts(sensory.cell_class)
    chordotonal = frame.loc[frame.cell_class.eq("chordotonal_organ_neuron")]
    result["chordotonal_superclass_counts"] = counts(chordotonal.super_class)
    result["chordotonal_subclass_counts"] = counts(chordotonal.cell_sub_class)
    result["motor_body_part_counts"] = counts(motor.body_part_effector)
    result["motor_function_counts"] = counts(motor.cell_function)
    result["front_leg_motor_muscle_counts"] = counts(motor.loc[motor.body_part_effector.eq("front_leg"), "peripheral_target_type"])
    result["hemilineage_13B_rows"] = int(frame.hemilineage.eq("13B").sum())
    result["hemilineage_13B_warning"] = "Hemilineage membership does not establish correspondence to physiological 13B-alpha cells"
    comparable = frame.neurotransmitter_predicted.notna() & frame.neurotransmitter_verified.notna()
    conflicts = frame.loc[comparable].apply(
        lambda row: row.neurotransmitter_predicted not in
        {s.strip() for s in row.neurotransmitter_verified.split(",")}, axis=1)
    result["transmitter"] = {"predicted_counts": counts(frame.neurotransmitter_predicted),
                             "verified_counts": counts(frame.neurotransmitter_verified),
                             "both_present": int(comparable.sum()),
                             "predicted_not_in_verified_set": int(conflicts.sum()),
                             "universal_postsynaptic_receptor_map": False,
                             "cell_electrical_parameters_available": False}
    selected = frame.loc[frame.cell_type.isin(INSPECT_TYPES)]
    inspection = records(selected, ["banc_888_id", "root_id", "root_888", "cell_type", "side", "super_class",
                                    "proofread", "neurotransmitter_predicted", "neurotransmitter_verified"])
    leg = frame.loc[front_leg_mask(frame)]
    leg_inspection = records(leg, ["banc_888_id", "cell_type", "cell_sub_class", "side", "super_class", "hemilineage",
                                    "peripheral_target_type", "proofread", "neurotransmitter_predicted", "neurotransmitter_verified"])
    return result, inspection, leg_inspection


def inventory_male(frame, transmitters):
    frame = frame.copy()
    frame["bodyId"] = exact_ids(frame.bodyId)
    transmitters = transmitters.copy()
    transmitters["body"] = exact_ids(transmitters.body)
    joined = frame.merge(transmitters, left_on="bodyId", right_on="body", how="left", validate="one_to_one", indicator=True)
    result = {"primary_key": "bodyId", "counts_are": "Annotation rows; includes fragments and non-neural segments",
              "superclass_counts": counts(frame.superclass), "status_counts": counts(frame.status),
              "status_label_counts": counts(frame.statusLabel), "class_counts": counts(frame["class"]),
              "transmitter_join_matched": int(joined["_merge"].eq("both").sum()),
              "transmitter_annotation_missing": int(joined["_merge"].eq("left_only").sum()),
              "transmitter_rows_outside_annotation_table": int((~transmitters.body.isin(frame.bodyId)).sum()),
              "consensus_nt_counts_on_annotation_rows": counts(joined.consensus_nt),
              "receptor_type_counts": counts(frame.receptorType),
              "universal_postsynaptic_receptor_map": False,
              "cell_electrical_parameters_available": False, "targets": {}, "bilateral_ambiguities": []}
    for cell_type in TARGETS:
        target = frame.loc[frame.type.eq(cell_type)]
        result["targets"][cell_type] = {"rows": len(target), "sides": counts(target.rootSide)}
        if len(target) == 2 and set(target.rootSide.dropna()) != {"L", "R"}:
            result["bilateral_ambiguities"].append(cell_type)
    selected = joined.loc[joined.type.isin(INSPECT_TYPES)]
    return result, records(selected, ["bodyId", "type", "rootSide", "somaSide", "superclass", "statusLabel", "consensus_nt", "ground_truth"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=ROOT / "data/anatomy-feasibility-v1")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/brain-integration/banc-feasibility-v1")
    parser.add_argument("--fetch-schemas", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    receipt_path = args.report / "source-access.json"
    receipt = json.loads(receipt_path.read_text())
    frames, tables = {}, {}
    for name in ("banc_888_meta.feather", "banc_888_metrics.feather",
                 "body-annotations-male-cns-v1.0-minconf-0.5.feather", "body-neurotransmitters-male-cns-v1.0.feather"):
        frames[name], tables[name] = verified_frame(args.cache, receipt, name)
    banc, banc_roots, leg_roots = inventory_banc(frames["banc_888_meta.feather"], frames["banc_888_metrics.feather"])
    male, male_roots = inventory_male(frames["body-annotations-male-cns-v1.0-minconf-0.5.feather"],
                                      frames["body-neurotransmitters-male-cns-v1.0.feather"])
    inventory = {"schema_version": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                 "script_sha256": digest(Path(__file__)), "source_receipt_sha256": digest(receipt_path),
                 "access_helper_sha256": digest(Path(__file__).with_name("assess_cns_feasibility.py")),
                 "scope": "Annotation inventory only; no edges, dynamics, or fitted responses",
                 "tables": tables, "banc": banc, "male": male,
                 "runtime_seconds": time.monotonic() - started,
                 "peak_process_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * (1 if sys.platform == "darwin" else 1024),
                 "runtime_scope": "Hash checking, annotation decoding, inventory and joins; excludes neural/physics simulation"}
    write_json(args.report / "annotation-inventory.json", inventory)
    write_json(args.report / "selected-identities.json", {
        "schema_version": 1, "warning": "Candidate inspection roster, not a sensory or motor adapter. No cross-dataset state transfer.",
        "banc_v888_archived": banc_roots, "male_cns_v1": male_roots})
    write_json(args.report / "front-leg-identities.json", {
        "schema_version": 1, "warning": "Inspection roster only; muscle mechanics, subgroup physiology and exact connectivity not yet qualified.",
        "dataset": "BANC", "materialization": 888, "annotation_sha256": tables["banc_888_meta.feather"]["sha256"],
        "rows": leg_roots})
    if args.fetch_schemas:
        schemas = {}
        for key, info in receipt["graph_probes"].items():
            raw = range_get(info, 0, 8192)
            schemas[key] = {"url": info["url"], "etag": info["etag"], "range_bytes_read": len(raw),
                            "schema": str(pa.ipc.read_schema(pa.BufferReader(raw[8:])))}
        write_json(args.report / "graph-schema.json", schemas)
    print(json.dumps({"banc_rows": tables["banc_888_meta.feather"]["rows"],
                      "male_rows": tables["body-annotations-male-cns-v1.0-minconf-0.5.feather"]["rows"],
                      "banc_root_mismatches": banc["generic_root_mismatches"],
                      "banc_bilateral_ambiguities": banc["bilateral_ambiguities"],
                      "male_nt_matched": male["transmitter_join_matched"]}))


if __name__ == "__main__":
    main()

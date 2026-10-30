"""End-to-end T-1 *reviewed candidate* export; no production clearance."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from src.pipeline import run_directory
from src.eligibility import dhan_mapping
from src.dhan_controls import load_broker_controls
from src.restriction_inputs import read_control, combine_controls

def produce(asof, target, input_dir, config_path, dhan_path, controls, output_dir):
    if target <= asof:
        raise ValueError("Target date must be later than as-of session")
    result = run_directory(input_dir, asof, config_path)
    mapping = dhan_mapping(dhan_path)
    broker_flags = load_broker_controls(dhan_path)
    control_maps=[]
    source_manifest=list(result["source_manifest"])
    for p in controls:
        entries, meta = read_control(p, target)
        control_maps.append(entries)
        source_manifest.append({"type":"normalized_control", **meta})
    # At least two distinct independently sourced controls must be supplied.
    if len(controls) < 2 or len(set(map(str, controls))) != len(controls):
        raise ValueError("Two distinct verified controls are required")
    isins=[d["isin"] for d in result["decisions"]]
    effective=combine_controls(isins, control_maps)
    output=[]
    for original in result["decisions"]:
        row=dict(original)
        ids=mapping.get(row["isin"],[])
        control=effective[row["isin"]]
        if not row.get("liquidity_pass"):
            row["status"]="EXCLUDED_LIQUIDITY_OR_HISTORY"
        elif len(ids)!=1:
            row["status"]="HOLD_DHAN_MAPPING"
        elif row["isin"] not in broker_flags or broker_flags[row["isin"]]["status"] == "HOLD_BROKER_FLAGS":
            row["status"]="HOLD_BROKER_FLAGS"
        elif broker_flags[row["isin"]]["status"] == "BLOCK_BROKER_SURVEILLANCE":
            row["status"]="EXCLUDED_BROKER_SURVEILLANCE"
        elif control["action"]=="BLOCK":
            row["status"]="EXCLUDED_RESTRICTION"
        elif control["action"]!="ALLOW":
            row["status"]="HOLD_RESTRICTION_VALIDATION"
        else:
            row["status"]="REVIEWED_CANDIDATE_NOT_PRODUCTION_APPROVED"
            row["dhan_security_id"]=ids[0]
        output.append(row)
    source_manifest.append({"type":"dhan_instruments", "sha256": hashlib.sha256(Path(dhan_path).read_bytes()).hexdigest()})
    tally=dict(Counter(item["status"] for item in output))
    package={"asof_date":asof,"target_date":target,"approval_state":"REVIEWED_ONLY",
             "source_manifest":source_manifest,"status_counts":tally,"decisions":output}
    path=Path(output_dir)
    path.mkdir(parents=True,exist_ok=True)
    target_file=path/"reviewed_candidates.json"
    target_file.write_text(json.dumps(package,indent=2,default=str),encoding="utf-8")
    return package

def main():
    p=argparse.ArgumentParser()
    for arg in ("asof","target","input-dir","dhan","output-dir"):
        p.add_argument("--"+arg,required=True)
    p.add_argument("--control",action="append",required=True)
    p.add_argument("--config",default="config/universe.yaml")
    a=p.parse_args()
    try:
        result=produce(a.asof,a.target,a.input_dir,a.config,a.dhan,a.control,a.output_dir)
    except (ValueError,OSError,KeyError) as exc:
        p.exit(2, f"NOT_READY: {exc}\n")
    print(json.dumps({"approval_state":result["approval_state"],"status_counts":result["status_counts"]},indent=2))

if __name__=="__main__":
    main()

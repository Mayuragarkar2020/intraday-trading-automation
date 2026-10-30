"""Research-only broker mapping statistics for a genuine NSE liquidity report."""
import argparse
import json
from collections import Counter
from pathlib import Path
from src.source_verification import fetch_dhan_master
from src.eligibility import dhan_mapping
from src.dhan_controls import load_broker_controls

def reconcile(report, mapping, broker):
    rows=[r for r in report["decisions"] if r.get("liquidity_pass") is True]
    out=[]
    for r in rows:
        isin=r["isin"]
        ids=mapping.get(isin,[])
        detail=broker.get(isin)
        if len(ids)!=1:
            status="HOLD_NON_UNIQUE_DHAN_MAPPING"
        elif detail is None:
            status="HOLD_MISSING_BROKER_CONTROLS"
        elif detail["status"]!="BROKER_FLAGS_CLEAR":
            status=detail["status"]
        else:
            status="BROKER_CLEARED_NSE_RESTRICTIONS_PENDING"
        out.append({"isin":isin,"symbol":r["symbol"],"status":status,
                    "security_id": ids[0] if len(ids)==1 else None})
    return {"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "asof_date":report["asof_date"],
            "summary":dict(Counter(r["status"] for r in out)),
            "candidates":out}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="output/live_liquidity_report.json")
    p.add_argument("--dhan-file",default="data/raw/dhan-detailed.csv")
    p.add_argument("--output",default="output/dhan_reconciliation.json")
    args=p.parse_args()
    report=json.loads(Path(args.input).read_text())
    if report.get("approval_state")!="RESEARCH_ONLY_NO_TRADING":
        raise ValueError("Only research reports are allowed")
    source=fetch_dhan_master(args.dhan_file)
    result=reconcile(report,dhan_mapping(args.dhan_file),load_broker_controls(args.dhan_file))
    result["source_manifest"]=source
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps({"asof_date":result["asof_date"],"summary":result["summary"],
                      "approval_state":result["approval_state"]}))

if __name__=="__main__":
    main()

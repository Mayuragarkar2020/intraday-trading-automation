"""Research-only live historical pipeline: explicit 20 NSE sessions, no approval."""
import argparse
import json
from pathlib import Path
from scripts.download_20_sessions import download
from src.pipeline import run_directory

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dates-file",required=True)
    p.add_argument("--asof",required=True)
    p.add_argument("--directory",default="data/raw/nse")
    p.add_argument("--output",default="output/live_liquidity_report.json")
    p.add_argument("--config",default="config/universe.yaml")
    a=p.parse_args()
    manifests=download(a.dates_file,a.directory)
    result=run_directory(a.directory,a.asof,a.config)
    if len(result["session_dates"])!=20:
        raise ValueError("Incomplete trading session set")
    counts={}
    for row in result["decisions"]:
        k=row["status"]
        counts[k]=counts.get(k,0)+1
    report={"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "asof_date":a.asof,"session_dates":result["session_dates"],
            "source_manifest":manifests,"counts":counts,
            "liquidity_pass_count":sum(x.get("liquidity_pass",False) for x in result["decisions"]),
            "decisions":result["decisions"]}
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"approval_state":report["approval_state"],
                      "asof_date":a.asof,"counts":counts,
                      "liquidity_pass_count":report["liquidity_pass_count"]}))
if __name__=="__main__":
    main()

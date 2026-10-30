"""Live source readiness diagnostic, never an eligibility approval."""
import argparse,json
from pathlib import Path
from src.source_readiness import evaluate_readiness

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asof",required=True)
    p.add_argument("--surveillance-date",required=True)
    p.add_argument("--output",default="output/source_readiness.json")
    args=p.parse_args()
    report=evaluate_readiness(args.asof,args.surveillance_date)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"states":{k:v["state"] for k,v in report["checks"].items()}}))
    return 0 if report["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY" else 2

if __name__=="__main__":
    raise SystemExit(main())

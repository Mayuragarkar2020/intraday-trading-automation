"""Live source readiness diagnostic, never an eligibility approval."""
import argparse,json
from pathlib import Path
from src.source_readiness import retry_readiness

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asof",required=True)
    p.add_argument("--surveillance-date",required=True)
    p.add_argument("--output",default="output/source_readiness.json")
    p.add_argument("--attempts",type=int,default=3)
    p.add_argument("--retry-delay",type=int,default=10)
    args=p.parse_args()
    report=retry_readiness(args.asof,args.surveillance_date,attempts=args.attempts,delay_seconds=args.retry_delay)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"states":{k:v["state"] for k,v in report["checks"].items()},"attempts_used":report["attempts_used"]}))
    return 0 if report["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY" else 2

if __name__=="__main__":
    raise SystemExit(main())

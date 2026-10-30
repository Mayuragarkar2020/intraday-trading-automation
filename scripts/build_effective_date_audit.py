"""Generate source-specific effective-date audit from readiness results; never self-approve."""
import argparse,json
from pathlib import Path
from src.exchange_calendar import next_regular_session
from src.effective_date_policy import REQUIRED,validate_manifest

def build(readiness):
    asof=readiness["asof_date"]
    target=next_regular_session(asof)
    checks=readiness.get("checks",{})
    sources={}
    for name in REQUIRED:
        found=checks.get(name,{})
        sources[name]={
          "source_session":asof if found.get("state")=="AVAILABLE" else None,
          "effective_for_session":None,
          "evidence_reviewed":False,
          "sha256":found.get("sha256"),
          "source_url":found.get("url"),
          "availability_state":found.get("state","MISSING"),
          "review_note":"Requires official evidence of applicability to target session"
        }
    manifest={"asof_date":asof,"target_date":target,"sources":sources}
    return {"manifest":manifest,"evaluation":validate_manifest(manifest,asof,target)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--readiness",default="output/source_readiness.json")
    p.add_argument("--output",default="output/effective_date_audit.json")
    args=p.parse_args()
    result=build(json.loads(Path(args.readiness).read_text()))
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2))
    print(json.dumps({"target":result["manifest"]["target_date"],"source_evidence_complete":result["evaluation"]["source_evidence_complete"],"decisions":result["evaluation"]["decisions"]}))
if __name__=="__main__":main()

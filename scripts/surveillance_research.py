"""Read actual NSE historical REG_IND and classify liquidity-qualified stocks."""
import argparse,json,urllib.request
from src.source_dates import report_names
from collections import Counter
from pathlib import Path
from src.nse_surveillance import load_surveillance,classify

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--surveillance-date",required=True)
    args=parser.parse_args()
    report=json.loads(Path("output/live_liquidity_report.json").read_text())
    name=report_names(report["asof_date"],args.surveillance_date)["surveillance"]
    url="https://nsearchives.nseindia.com/content/cm/"+name
    p=Path("data/raw")/name;p.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as res:
        data=res.read(2_000_001)
    if not data or len(data)>2_000_000:raise ValueError("Invalid surveillance report")
    p.write_bytes(data)
    surveillance=load_surveillance(p)
    if report.get("approval_state")!="RESEARCH_ONLY_NO_TRADING":raise ValueError("Unexpected report approval state")
    rows=[{"symbol":r["symbol"],"status":classify(r["symbol"],surveillance)} for r in report["decisions"] if r.get("liquidity_pass")]
    result={"approval_state":"RESEARCH_ONLY_NO_TRADING","counts":dict(Counter(x["status"] for x in rows)),"rows":rows}
    target=Path("output/surveillance_research.json");target.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["counts"]))
if __name__=="__main__":main()

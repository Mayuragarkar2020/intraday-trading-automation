"""Read actual NSE historical REG_IND and classify liquidity-qualified stocks."""
import json,urllib.request
from collections import Counter
from pathlib import Path
from src.nse_surveillance import load_surveillance,classify

URL="https://nsearchives.nseindia.com/content/cm/REG_IND250926.csv"
def main():
    p=Path("data/raw/REG_IND250926.csv");p.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as res:
        data=res.read(2_000_001)
    if not data or len(data)>2_000_000:raise ValueError("Invalid surveillance report")
    p.write_bytes(data)
    surveillance=load_surveillance(p)
    report=json.loads(Path("output/live_liquidity_report.json").read_text())
    if report["asof_date"]!="2026-09-25":raise ValueError("Unexpected research date")
    rows=[{"symbol":r["symbol"],"status":classify(r["symbol"],surveillance)} for r in report["decisions"] if r.get("liquidity_pass")]
    result={"approval_state":"RESEARCH_ONLY_NO_TRADING","counts":dict(Counter(x["status"] for x in rows)),"rows":rows}
    target=Path("output/surveillance_research.json");target.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["counts"]))
if __name__=="__main__":main()

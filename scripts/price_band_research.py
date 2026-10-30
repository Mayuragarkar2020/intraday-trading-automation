import argparse,json,urllib.request
from pathlib import Path
from collections import Counter
from src.nse_price_bands import parse_complete,parse_changes,classify
BASE="https://nsearchives.nseindia.com/content/equities/"
def fetch(filename):
    req=urllib.request.Request(BASE+filename,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as r:data=r.read(3000001)
    if not data or len(data)>3000000:raise ValueError("Invalid NSE report")
    p=Path("data/raw/bands")/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return p
def main():
    p=argparse.ArgumentParser();p.add_argument("--report",default="output/live_liquidity_report.json");p.add_argument("--output",default="output/band_research.json");a=p.parse_args()
    report=json.loads(Path(a.report).read_text())
    if report["asof_date"]!="2026-09-25":raise ValueError("Date mismatch")
    full=parse_complete(fetch("sec_list_25092026.csv"))
    changes=parse_changes(fetch("eq_band_changes_25092026.csv"))
    rows=[{"symbol":r["symbol"],"isin":r["isin"],"band_result":classify(r["symbol"],full,changes)} for r in report["decisions"] if r.get("liquidity_pass")]
    result={"approval_state":"RESEARCH_ONLY_NO_TRADING","counts":dict(Counter(x["band_result"] for x in rows)),"rows":rows}
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["counts"]))
if __name__=="__main__":main()

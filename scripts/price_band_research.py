import argparse,json,urllib.request,urllib.error
from pathlib import Path
from collections import Counter
from src.nse_price_bands import parse_complete,parse_changes,classify
from src.source_dates import report_names
BASE="https://nsearchives.nseindia.com/content/equities/"
def fetch(filename):
    req=urllib.request.Request(BASE+filename,headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:data=r.read(3000001)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"NOT_READY: required NSE price-band source {filename} returned HTTP {exc.code}; no prior-day fallback permitted") from exc
    if not data or len(data)>3000000:raise ValueError("Invalid NSE report")
    p=Path("data/raw/bands")/filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return p
def main():
    p=argparse.ArgumentParser();p.add_argument("--report",default="output/live_liquidity_report.json");p.add_argument("--output",default="output/band_research.json");p.add_argument("--surveillance-date",required=True);a=p.parse_args()
    report=json.loads(Path(a.report).read_text())
    if report["asof_date"] is None:raise ValueError("Missing asof date")
    names=report_names(report["asof_date"],a.surveillance_date)
    # Require both same-session source files; partial publication is never approval.
    missing=[]
    sources={}
    for key in ("price_band_complete","price_band_changes"):
        try:
            sources[key]=fetch(names[key])
        except RuntimeError as exc:
            missing.append(str(exc))
    if missing:
        raise RuntimeError("NOT_READY: incomplete same-session band sources: "+"; ".join(missing))
    full=parse_complete(sources["price_band_complete"])
    changes=parse_changes(sources["price_band_changes"])
    rows=[{"symbol":r["symbol"],"isin":r["isin"],"band_result":classify(r["symbol"],full,changes)} for r in report["decisions"] if r.get("liquidity_pass")]
    result={"approval_state":"RESEARCH_ONLY_NO_TRADING","counts":dict(Counter(x["band_result"] for x in rows)),"rows":rows}
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2))
    print(json.dumps(result["counts"]))
if __name__=="__main__":main()

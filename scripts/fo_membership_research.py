"""Research-only NSE F&O membership crosscheck for No Band cash equities.

Historical membership from stock futures/options records in same-date F&O UDiFF.
Does not certify price-band eligibility or dynamic-limit execution.
"""
import csv,io,json,urllib.request,zipfile,hashlib
from collections import Counter
from pathlib import Path

def get_membership(asof):
    compact=asof.replace("-","")
    url=f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{compact}_F_0000.csv.zip"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=45) as r:raw=r.read(10_000_001)
    if len(raw)>10_000_000 or len(raw)<500:raise ValueError("Invalid F&O archive size")
    members=set()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names=[name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names)!=1:raise ValueError("Expected exactly one F&O CSV")
        with archive.open(names[0]) as f:
            rd=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig"))
            if not {"TradDt","FinInstrmTp","TckrSymb"}.issubset(rd.fieldnames or []):
                raise ValueError("Unexpected F&O schema")
            for row in rd:
                if row["TradDt"].strip()!=asof:raise ValueError("Incorrect derivative source date")
                if row["FinInstrmTp"].strip() in {"STF","STO"}:
                    symbol=row["TckrSymb"].strip()
                    if not symbol:raise ValueError("Blank stock derivative symbol")
                    members.add(symbol)
    if not members:raise ValueError("No stock derivative underlyings discovered")
    return members,{"source_url":url,"source_sha256":hashlib.sha256(raw).hexdigest(),
                    "member_count":len(members),"asof_date":asof}

def assess(report, membership):
    if report.get("approval_state")!="RESEARCH_ONLY_NO_TRADING":
        raise ValueError("Untrusted price band report")
    rows=[]
    for r in report["rows"]:
        if r["band_result"] not in ("HOLD_FO_MEMBERSHIP_UNVERIFIED","HOLD_UNCLASSIFIED_BAND"):
            continue
        status=("DYNAMIC_BAND_FO_RESEARCH_ONLY" if r["symbol"] in membership
                else "HOLD_NO_BAND_NOT_IN_FO")
        rows.append({"symbol":r["symbol"],"isin":r["isin"],"status":status})
    return {"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "counts":dict(Counter(r["status"] for r in rows)),"rows":rows}

def main():
    bands=json.loads(Path("output/band_research.json").read_text())
    members,manifest=get_membership("2026-09-25")
    result=assess(bands,members);result["manifest"]=manifest
    dest=Path("output/fo_membership_research.json")
    dest.write_text(json.dumps(result,indent=2))
    print(json.dumps({"approval_state":result["approval_state"],"counts":result["counts"],
                      "source_date":manifest["asof_date"]}))
if __name__=="__main__":main()

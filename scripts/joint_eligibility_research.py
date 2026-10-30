"""Combine independent research findings; never generates trade approvals."""
from collections import Counter
import json
from pathlib import Path

def combine(liquidity, broker, bands, surveillance):
    if liquidity.get("approval_state")!="RESEARCH_ONLY_NO_TRADING":
        raise ValueError("Liquidity report not marked research-only")
    if any(x.get("approval_state")!="RESEARCH_ONLY_NO_TRADING" for x in (broker,bands,surveillance)):
        raise ValueError("A component is not research-only")
    by_broker={x["isin"]:x for x in broker["candidates"]}
    by_bands={x["isin"]:x for x in bands["rows"]}
    by_surv={x["symbol"]:x for x in surveillance["rows"]}
    output=[]
    for row in liquidity["decisions"]:
        if not row.get("liquidity_pass"): continue
        isin=row["isin"];symbol=row["symbol"]
        b=by_broker.get(isin,{}).get("status","HOLD_BROKER_MISSING")
        p=by_bands.get(isin,{}).get("band_result","HOLD_BAND_MISSING")
        s=by_surv.get(symbol,{}).get("status","HOLD_SURVEILLANCE_MISSING")
        if p=="EXCLUDED_NARROW_BAND":
            state="EXCLUDED_NARROW_BAND"
        elif b not in {"BROKER_CLEARED_NSE_RESTRICTIONS_PENDING"}:
            state="HOLD_BROKER"
        elif p!="BAND_SCREEN_PASSED" or s!="SURVEILLANCE_BASIC_CLEAR":
            state="HOLD_EXCHANGE_VERIFICATION"
        else:
            state="CANDIDATE_BASIC_CHECKS_PASSED_NOT_APPROVED"
        output.append({"isin":isin,"symbol":symbol,"broker":b,"price_band":p,
                       "surveillance":s,"combined_status":state})
    if len(output)!=sum(bool(r.get("liquidity_pass")) for r in liquidity["decisions"]):
        raise ValueError("Incomplete joint audit")
    return {"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "asof_date":liquidity["asof_date"],"count":len(output),
            "counts":dict(Counter(x["combined_status"] for x in output)),"rows":output}

def main():
    root=Path("output")
    read=lambda p: json.loads((root/p).read_text())
    result=combine(read("live_liquidity_report.json"),
                   read("dhan_reconciliation.json"),
                   read("band_research.json"),
                   read("surveillance_research.json"))
    (root/"joint_eligibility_research.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({"approval_state":result["approval_state"],"counts":result["counts"]}))
if __name__=="__main__":main()

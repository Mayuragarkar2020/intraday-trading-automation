"""Sensitivity analysis from actual screened output. No production approvals."""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path

def analyze(report):
    thresholds=(50,100,200)
    rows=[r for r in report["decisions"] if "metrics" in r]
    results=[]
    for threshold in thresholds:
        selected=[]
        for r in rows:
            m=r["metrics"]
            if (Decimal(m["avg_turnover_20d_cr"]) >= threshold
                and Decimal(m["median_turnover_20d_cr"]) >= 50
                and Decimal(m["last_turnover_cr"]) >= 75
                and Decimal(m["activity_ratio"]) >= Decimal("0.75")
                and Decimal(m["min_turnover_5d_cr"]) >= 30
                and Decimal(m["close"]) >= 300
                and Decimal(m["close"]) <= 5000):
                # Original screening also requires all sessions with positive volume.
                if Decimal(m["avg_volume_20d"]) > 0:
                    selected.append(r)
        results.append({"minimum_average_turnover_cr":threshold,
                        "candidate_count":len(selected),
                        "symbols":[r["symbol"] for r in selected]})
    return {"asof_date":report["asof_date"],
            "approval_state":"RESEARCH_ONLY_NO_TRADING",
            "thresholds":results}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="output/live_liquidity_report.json")
    p.add_argument("--output",default="output/liquidity_sensitivity.json")
    a=p.parse_args()
    data=json.loads(Path(a.input).read_text())
    if data.get("approval_state")!="RESEARCH_ONLY_NO_TRADING":
        raise ValueError("Input is not a validated research report")
    result=analyze(data)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2))
    print(json.dumps({r["minimum_average_turnover_cr"]:r["candidate_count"] for r in result["thresholds"]}))
if __name__=="__main__":
    main()

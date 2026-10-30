from scripts.analyze_liquidity_sensitivity import analyze

def row(avg):
    return {"symbol":"ABC","metrics":{"avg_turnover_20d_cr":str(avg),
      "median_turnover_20d_cr":"90","last_turnover_cr":"100",
      "activity_ratio":"1","min_turnover_5d_cr":"50",
      "close":"1000","avg_volume_20d":"1000000"}}

def test_thresholds_monotone():
    report={"asof_date":"2026-09-25","decisions":[row(80),row(150),row(250)]}
    results=analyze(report)["thresholds"]
    assert [r["candidate_count"] for r in results]==[3,2,1]

import csv
from datetime import date,timedelta
from scripts.produce_reviewed_universe import produce

def test_candidate_export_cannot_claim_production_approval(tmp_path):
    root=tmp_path/"prices";root.mkdir()
    dates=[(date(2026,9,1)+timedelta(days=i)).isoformat() for i in range(20)]
    for day in dates:
        with (root/("nse_"+day+".csv")).open("w",newline="") as f:
            w=csv.writer(f);w.writerow(["TckrSymb","SctySrs","ISIN","TradDt","ClsPric","TtlTradgVol","TtlTrfVal"])
            w.writerow(["ABC","EQ","INE000A01000",day,"1000","1200000","1200000000"])
    dhan=tmp_path/"dhan.csv"
    with dhan.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["EXCH_ID","SEGMENT","ISIN","SERIES","SECURITY_ID"])
        w.writerow(["NSE","E","INE000A01000","EQ","101"])
    controls=[]
    for i in (1,2):
        path=tmp_path/("control"+str(i)+".csv")
        with path.open("w",newline="") as f:
            w=csv.writer(f);w.writerow(["isin","target_date","action","reason"])
            w.writerow(["INE000A01000","2026-10-01","ALLOW",""])
        controls.append(str(path))
    config=tmp_path/"config.yaml"
    config.write_text("universe:\n  required_history_sessions: 20\n  price_min: 300\n  price_max: 5000\nliquidity:\n  avg_turnover_20d_min_cr: 100\n  median_turnover_20d_min_cr: 50\n  last_turnover_min_cr: 75\n  last_to_avg_ratio_min: 0.75\n  min_turnover_5d_cr: 30\n")
    result=produce(dates[-1],"2026-10-01",str(root),str(config),str(dhan),controls,str(tmp_path/"out"))
    import json
    saved=json.loads((tmp_path/"out"/"reviewed_candidates.json").read_text())
    assert saved["approval_state"]=="REVIEWED_ONLY"
    assert result["approval_state"]=="REVIEWED_ONLY"
    assert result["decisions"][0]["status"]=="REVIEWED_CANDIDATE_NOT_PRODUCTION_APPROVED"

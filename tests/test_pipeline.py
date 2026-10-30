import csv
from decimal import Decimal
from datetime import date, timedelta
import pytest
from src.pipeline import screen_files
from src.ingestion import DataQualityError

CFG = {"universe":{"price_min":300,"price_max":5000,"required_history_sessions":20},
       "liquidity":{"avg_turnover_20d_min_cr":100,"median_turnover_20d_min_cr":50,
                    "last_turnover_min_cr":75,"last_to_avg_ratio_min":0.75,
                    "min_turnover_5d_cr":30}}

def write_files(tmp_path):
    paths=[]
    dates=[(date(2026,9,28)+timedelta(days=i)).isoformat() for i in range(20)]
    for day in dates:
        p=tmp_path/f"nse_{day}.csv"
        with p.open("w",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["TckrSymb","SctySrs","ISIN","TradDt","ClsPric","TtlTradgVol","TtlTrfVal"])
            writer.writerow(["ABC","EQ","INE000A01000",day,"1000","1200000","1200000000"])
        paths.append(str(p))
    return paths,dates

def test_provisional_universe_never_approves_without_restrictions(tmp_path):
    paths, dates=write_files(tmp_path)
    result=screen_files(paths,dates[-1],CFG)
    assert result["eligible_count"]==0
    assert result["hold_count"]==1
    assert result["decisions"][0]["status"]=="HOLD_RESTRICTIONS_AND_MAPPING"

def test_incomplete_history_fails_closed(tmp_path):
    paths,dates=write_files(tmp_path)
    with pytest.raises(DataQualityError):
        screen_files(paths[:-1],dates[-1],CFG)

def test_wrong_asof_fails_closed(tmp_path):
    paths,dates=write_files(tmp_path)
    with pytest.raises(DataQualityError):
        screen_files(paths,dates[-2],CFG)

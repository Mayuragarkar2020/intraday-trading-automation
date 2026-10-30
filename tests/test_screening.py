from decimal import Decimal
from src.screening import evaluate, provisional_status

CFG = {"universe": {"price_min":300,"price_max":5000,"required_history_sessions":20},
       "liquidity":{"avg_turnover_20d_min_cr":100,"median_turnover_20d_min_cr":50,
                    "last_turnover_min_cr":75,"last_to_avg_ratio_min":0.75,
                    "min_turnover_5d_cr":30}}

def rows(turnover_cr=120):
    return [{"isin":"INE000A01000","symbol":"ABC","date":f"2026-10-{i:02d}",
             "close":Decimal(1000),"volume":1000000,
             "turnover_inr":Decimal(turnover_cr)*Decimal(10000000)} for i in range(1,21)]

def test_liquid_stock_still_held_until_restrictions_verified():
    result=evaluate(rows(),CFG)
    assert result["liquidity_pass"]
    assert provisional_status(result)=="HOLD_RESTRICTIONS_AND_MAPPING"

def test_low_turnover_excluded():
    result=evaluate(rows(10),CFG)
    assert not result["liquidity_pass"]
    assert "L01_AVG20" in result["failed_rules"]

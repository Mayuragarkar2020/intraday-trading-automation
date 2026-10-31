from datetime import datetime,timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from src.candle_input import CandleInput
from src.dhan_verified_indicators import calculate_session_indicators,historical_relative_volume

IST=ZoneInfo("Asia/Kolkata")
def session(day,volume=100):
    t=datetime.fromisoformat(day+"T09:20:00+05:30")
    return [CandleInput(time=(t+timedelta(minutes=5*i)).isoformat(),
       open=Decimal("100"),high=Decimal("101"),low=Decimal("99"),
       close=Decimal("100"),volume=volume) for i in range(72)]

def test_indicators_computed_from_complete_sessions():
    result=calculate_session_indicators([session("2026-10-28")],session("2026-10-29"))
    assert result["ema10"]=="100"
    assert result["ema20"]=="100"
    assert result["session_vwap"]=="100"
    assert result["vwap_accounting_verified"] is True
    assert result["qualified_for_trading"] is False

def test_missing_opening_candle_blocks_calculation():
    with pytest.raises(ValueError,match="opening"):
        calculate_session_indicators([session("2026-10-28")[1:]],session("2026-10-29"))

def test_relative_volume_requires_20_prior_sessions():
    with pytest.raises(ValueError,match="20 prior"):
        historical_relative_volume([session("2026-10-28")],session("2026-10-29"),"09:25")

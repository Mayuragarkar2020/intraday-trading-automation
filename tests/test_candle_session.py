from decimal import Decimal as D
from datetime import datetime,timedelta,timezone
import pytest
from src.candle_pipeline import Candle
from src.session_vwap import session_vwap
from src.candle_session import ensure_ordered_session
from src.setup_detector import Bar,detect_setup

def candles(times):
    return [Candle(t,D("100"),D("102"),D("98"),D("100"),100) for t in times]

def test_session_vwap_same_day():
    items=candles(["2026-11-02T09:20:00+05:30","2026-11-02T09:25:00+05:30","2026-11-02T09:30:00+05:30"])
    assert session_vwap(items)==D("100")

def test_session_vwap_rejects_gap_and_cross_session():
    with pytest.raises(ValueError):
        session_vwap(candles(["2026-11-02T09:20:00+05:30","2026-11-02T09:30:00+05:30"]))
    with pytest.raises(ValueError):
        session_vwap(candles(["2026-11-02T15:30:00+05:30","2026-11-03T09:20:00+05:30"]))
    with pytest.raises(ValueError):
        session_vwap(candles(["2026-11-02T09:20:00","2026-11-02T09:25:00"]))

def test_too_wide_range_blocks_arming():
    def b(t,h,l):
        return Bar(t,D("100"),D(h),D(l),D("100"),1000,D("99"),D("98"),D("97"),D("2"),True)
    x=detect_setup([b("1","105","99"),b("2","106","99"),b("3","104","99")])
    assert x.reason=="CONSOLIDATION_RANGE_TOO_WIDE"

def test_cross_session_setup_rejected():
    def b(t):
        return Bar(t,D("100"),D("101"),D("99"),D("100"),1000,D("98"),D("97"),D("96"),D("2"),True)
    x=detect_setup([b("2026-11-02T15:25:00+05:30"),b("2026-11-02T15:30:00+05:30"),b("2026-11-03T09:20:00+05:30")])
    assert x.reason=="INVALID_CANDLE_SESSION_OR_GAPS"

from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_candle_audit import audit_candles
IST=ZoneInfo("Asia/Kolkata")
def response(count):
    t=datetime(2026,10,29,9,15,tzinfo=IST)
    return {"timestamp":[int((t+timedelta(minutes=5*i)).timestamp()) for i in range(count)],
      "open":[100]*count,"high":[101]*count,"low":[99]*count,
      "close":[100]*count,"volume":[1000]*count}
def test_cas_72_candles_is_complete_with_research_assumption():
    r=audit_candles(response(72),as_of=datetime(2026,10,30,16,tzinfo=IST),timestamps_are_open=True,cas_eligible=True)
    assert r["sessions"][0]["session_complete"] is True
    assert r["sessions"][0]["expected_regular_session"]==72
    assert r["timestamp_convention_verified"] is False
    assert r["cas_eligibility_verified"] is False
def test_unverified_mode_does_not_approve():
    r=audit_candles(response(72),as_of=datetime(2026,10,30,16,tzinfo=IST),timestamps_are_open=True)
    assert r["sessions"][0]["session_complete"] is False
def test_genuine_early_gap_remains_flagged():
    p=response(72)
    for k in p:
        p[k]=p[k][1:]
    r=audit_candles(p,as_of=datetime(2026,10,30,16,tzinfo=IST),timestamps_are_open=True,cas_eligible=True)
    assert r["sessions"][0]["first_missing"]==["09:20"]
    assert r["sessions"][0]["session_complete"] is False

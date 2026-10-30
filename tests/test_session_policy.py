from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from src.session_policy import validate_dates,choose_next_session

IST=ZoneInfo("Asia/Kolkata")
def test_weekend_target_rejected():
    with pytest.raises(ValueError):
        validate_dates("2026-10-30","2026-10-31",datetime(2026,10,30,18,tzinfo=IST))
def test_unfinished_session_rejected():
    with pytest.raises(ValueError):
        validate_dates("2026-10-30","2026-11-02",datetime(2026,10,30,15,tzinfo=IST))
def test_calendar_resolves_holiday():
    days=["2026-10-30","2026-11-03","2026-11-04"]
    assert choose_next_session("2026-10-30",days)=="2026-11-03"
def test_no_calendar_proof_fails():
    with pytest.raises(ValueError):
        choose_next_session("2026-10-30",["2026-10-30"])

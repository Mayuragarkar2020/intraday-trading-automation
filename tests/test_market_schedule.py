from datetime import datetime
from zoneinfo import ZoneInfo
from src.market_schedule import research_window

IST=ZoneInfo("Asia/Kolkata")
def at(stamp):return datetime.fromisoformat(stamp).replace(tzinfo=IST)

def test_in_session():
    assert research_window(at("2026-11-02T09:45:00"))==(True,"RESEARCH_WINDOW")
def test_outside_session():
    assert research_window(at("2026-11-02T11:40:00"))[0] is False
def test_holiday_and_weekend():
    assert research_window(at("2026-11-10T10:00:00"))[1]=="MARKET_CLOSED"
    assert research_window(at("2026-11-08T10:00:00"))[1]=="MARKET_CLOSED"
def test_future_calendar_not_assumed():
    assert research_window(at("2027-01-04T10:00:00"))[1]=="CALENDAR_NOT_VERIFIED"

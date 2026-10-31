from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import pytest
from src.dhan_complete_sessions import fetch_complete_sessions

IST=ZoneInfo("Asia/Kolkata")
def fixture_bars(count=72,drop_first=False):
    t=datetime(2026,10,29,9,15,tzinfo=IST)
    ids=range(1 if drop_first else 0,count)
    stamps=[int((t+timedelta(minutes=5*i)).timestamp()) for i in ids]
    n=len(stamps)
    return {"timestamp":stamps,"open":[100]*n,"high":[101]*n,
            "low":[99]*n,"close":[100]*n,"volume":[1000]*n}

def test_padded_request_and_complete_session():
    called=[]
    def source(token,security_id,interval,start,end):
        called.append((start,end))
        return fixture_bars()
    days=fetch_complete_sessions("token","2885",["2026-10-29"],
                                 expected_bars=72,fetch=source,
                                 as_of=datetime(2026,10,31,10,tzinfo=IST))
    assert len(days[0])==72
    assert days[0][0].time[11:16]=="09:20"
    assert called==[("2026-10-28 09:15:00","2026-10-30 09:15:00")]

def test_missing_open_fails_closed():
    with pytest.raises(ValueError,match="Incomplete"):
        fetch_complete_sessions("token","2885",["2026-10-29"],
            expected_bars=72,fetch=lambda *args:fixture_bars(drop_first=True),
            as_of=datetime(2026,10,31,10,tzinfo=IST))

def test_incorrect_session_type_fails_closed():
    with pytest.raises(ValueError,match="Incomplete"):
        fetch_complete_sessions("token","2885",["2026-10-29"],
            expected_bars=75,fetch=lambda *args:fixture_bars(),
            as_of=datetime(2026,10,31,10,tzinfo=IST))

from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_rvol_research import validated_session_groups,research_rvol

IST=ZoneInfo("Asia/Kolkata")
def payload(days):
    times=[]
    for day in days:
        t=datetime.fromisoformat(day+"T09:15:00+05:30")
        times.extend(int((t+timedelta(minutes=5*i)).timestamp()) for i in range(72))
    n=len(times)
    return {"timestamp":times,"open":[100]*n,"high":[101]*n,"low":[99]*n,
            "close":[100]*n,"volume":[100]*n}
def test_complete_group():
    clean,rejected=validated_session_groups(payload(["2026-10-28","2026-10-29"]),
        as_of=datetime(2026,10,31,10,tzinfo=IST))
    assert len(clean)==2
    assert rejected==[]
def test_rvol_needs_20_prior_sessions():
    result=research_rvol("token","2885","2026-10-20 09:15:00","2026-10-30 15:30:00",
        as_of=datetime(2026,10,31,10,tzinfo=IST),
        fetch=lambda *a:payload(["2026-10-28","2026-10-29"]))
    assert result["status"]=="INSUFFICIENT_COMPLETE_SESSIONS"
    assert result["trading_approved"] is False

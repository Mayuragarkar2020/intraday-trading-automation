"""Read-only NSE historical candle quality audit for Dhan API data."""
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.candle_session import parse_close

IST=ZoneInfo("Asia/Kolkata")

def audit_candles(payload,*,as_of,timestamps_are_open):
    candles=normalize_dhan_intraday(payload,as_of=as_of,timestamps_are_open=timestamps_are_open)
    sessions=defaultdict(list)
    for c in candles:
        dt=parse_close(c.time)
        sessions[dt.date().isoformat()].append(dt)
    report=[]
    for day,times in sorted(sessions.items()):
        start=datetime.fromisoformat(day+"T09:20:00+05:30")
        expected=[start+timedelta(minutes=5*i) for i in range(75)]
        actual=set(times)
        missing=[t.strftime("%H:%M") for t in expected if t not in actual]
        report.append({"date":day,"received":len(times),"expected_regular_session":75,
                       "missing_count":len(missing),"first_missing":missing[:8],
                       "first_close":min(times).strftime("%H:%M"),
                       "last_close":max(times).strftime("%H:%M"),
                       "session_complete":len(missing)==0 and len(times)==75})
    return {"status":"AUDITED","candle_count":len(candles),
            "timestamp_assumption":"OPEN" if timestamps_are_open else "CLOSE",
            "timestamp_convention_verified":False,"sessions":report,
            "all_sessions_complete":bool(report) and all(x["session_complete"] for x in report),
            "execution_enabled":False}

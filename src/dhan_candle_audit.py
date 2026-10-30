"""Read-only NSE historical candle quality audit for Dhan API data."""
from collections import defaultdict
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.candle_session import parse_close

IST=ZoneInfo("Asia/Kolkata")

def audit_candles(payload,*,as_of,timestamps_are_open,cas_eligible=None):
    if cas_eligible is not None and type(cas_eligible) is not bool:
        raise ValueError("Invalid CAS eligibility")
    expected_count = 72 if cas_eligible is True else 75
    session_type = "CAS_CONTINUOUS" if cas_eligible is True else (
        "NON_CAS_CONTINUOUS" if cas_eligible is False else "UNVERIFIED")
    candles=normalize_dhan_intraday(payload,as_of=as_of,timestamps_are_open=timestamps_are_open)
    sessions=defaultdict(list)
    for c in candles:
        dt=parse_close(c.time)
        sessions[dt.date().isoformat()].append(dt)
    report=[]
    for day,times in sorted(sessions.items()):
        start=datetime.fromisoformat(day+"T09:20:00+05:30")
        expected=[start+timedelta(minutes=5*i) for i in range(expected_count)]
        actual=set(times)
        missing=[t.strftime("%H:%M") for t in expected if t not in actual]
        report.append({"date":day,"received":len(times),"expected_regular_session":expected_count,
                       "missing_count":len(missing),"first_missing":missing[:8],
                       "first_close":min(times).strftime("%H:%M"),
                       "last_close":max(times).strftime("%H:%M"),
                       "session_complete":cas_eligible is not None and len(missing)==0 and len(times)==expected_count})
    return {"status":"AUDITED","candle_count":len(candles),
            "timestamp_assumption":"OPEN" if timestamps_are_open else "CLOSE",
            "timestamp_convention_verified":False,"cas_eligibility_verified":False,
            "session_type_assumption":session_type,"sessions":report,
            "all_sessions_complete":bool(report) and all(x["session_complete"] for x in report),
            "execution_enabled":False}

"""Research-only RVOL check from Dhan, requiring twenty complete prior sessions.

Do not assume all calendar weekdays traded, or accept truncated sessions.
Observed complete sessions are an input study; no trade signals permitted.
"""
from collections import defaultdict
from datetime import datetime
from src.dhan_history_client import fetch_intraday
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.dhan_verified_indicators import historical_relative_volume
from src.candle_session import ensure_ordered_session

def validated_session_groups(payload,*,as_of,expected_bars=72):
    if expected_bars not in (72,75):raise ValueError("Session classification required")
    bars=normalize_dhan_intraday(payload,as_of=as_of,timestamps_are_open=True)
    groups=defaultdict(list)
    for bar in bars:groups[bar.time[:10]].append(bar)
    clean=[]
    rejected=[]
    for day,group in sorted(groups.items()):
        try:
            ensure_ordered_session([b.time for b in group])
            if len(group)!=expected_bars or group[0].time[11:16]!="09:20":
                raise ValueError("Partial session")
            clean.append(group)
        except ValueError:
            rejected.append(day)
    return clean,rejected

def research_rvol(token,security_id,from_date,to_date,*,as_of,expected_bars=72,
                  fetch=fetch_intraday):
    payload=fetch(token,security_id,5,from_date,to_date)
    clean,rejected=validated_session_groups(payload,as_of=as_of,expected_bars=expected_bars)
    if len(clean)<21:
        return {"status":"INSUFFICIENT_COMPLETE_SESSIONS",
                "complete_session_count":len(clean),"rejected_dates":rejected,
                "trading_approved":False}
    previous,current=clean[-21:-1],clean[-1]
    slot=current[-1].time[11:16]
    rvol=historical_relative_volume(previous,current,slot)
    return {"status":"RVOL_RESEARCH","date":current[0].time[:10],
            "slot":slot,"relative_volume":str(rvol),
            "prior_session_count":len(previous),"rejected_dates":rejected,
            "calendar_verified":False,"trading_approved":False}

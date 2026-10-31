"""Fetch validated complete Dhan five-minute sessions without inventing bars.

Uses an earlier calendar-day boundary because Dhan can omit the first candle
when the request starts exactly at market opening. No live/order endpoints.
"""
from datetime import date,datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_history_client import fetch_intraday
from src.dhan_candle_adapter import normalize_dhan_intraday

IST=ZoneInfo("Asia/Kolkata")

def fetch_complete_sessions(token,security_id,session_dates,*,expected_bars,
                            fetch=fetch_intraday,as_of=None):
    if expected_bars not in (72,75):raise ValueError("Explicit 72/75 session expectation required")
    if not session_dates or len(set(session_dates))!=len(session_dates):
        raise ValueError("Missing or duplicate dates")
    days=sorted(date.fromisoformat(d) for d in session_dates)
    if any(d.weekday()>=5 for d in days):
        raise ValueError("Holiday/weekend dates require separate trading calendar verification")
    start=days[0]-timedelta(days=1)
    end=days[-1]+timedelta(days=1)
    if end-start>timedelta(days=90):raise ValueError("Request exceeds 90 days")
    payload=fetch(token,security_id,5,start.strftime("%Y-%m-%d 09:15:00"),
                  end.strftime("%Y-%m-%d 09:15:00"))
    bars=normalize_dhan_intraday(payload,as_of=as_of or datetime.now(IST),
                                 timestamps_are_open=True)
    by_day={}
    for b in bars:by_day.setdefault(b.time[:10],[]).append(b)
    accepted=[]
    for day in session_dates:
        series=by_day.get(day,[])
        observed=[b.time[11:16] for b in series]
        baseline=datetime.combine(date.fromisoformat(day),datetime.min.time(),IST)
        expected=[(baseline+timedelta(hours=9,minutes=20+5*i)).strftime("%H:%M")
                  for i in range(expected_bars)]
        if observed!=expected:
            raise ValueError("Incomplete or irregular historical session: "+day)
        accepted.append(series)
    return accepted

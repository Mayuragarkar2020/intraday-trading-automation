"""NSE research-session scheduling. Cron runs are UTC; trade gating is IST.
Special sessions require an explicit reviewed schedule, never assumptions.
"""
from datetime import datetime,time
from zoneinfo import ZoneInfo

IST=ZoneInfo("Asia/Kolkata")
HOLIDAYS_2026=frozenset({
"2026-01-15","2026-01-26","2026-03-03","2026-03-26",
"2026-03-31","2026-04-03","2026-04-14","2026-05-01",
"2026-05-28","2026-06-26","2026-09-14","2026-10-02",
"2026-10-20","2026-11-10","2026-11-24","2026-12-25"})
def research_window(now,*,start=time(9,15),end=time(11,40)):
    if now.tzinfo is None:raise ValueError("Aware clock required")
    local=now.astimezone(IST)
    if local.year!=2026:return (False,"CALENDAR_NOT_VERIFIED")
    if local.weekday()>=5 or local.date().isoformat() in HOLIDAYS_2026:
        return (False,"MARKET_CLOSED")
    if not start<=local.time()<end:return (False,"OUTSIDE_RESEARCH_WINDOW")
    return (True,"RESEARCH_WINDOW")

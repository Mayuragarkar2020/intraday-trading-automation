"""Reviewed NSE capital-market 2026 holiday calendar.

Source: NSE/CMTR/71775, December 12, 2025.
An explicit annual source review is required; other years fail closed.
Special sessions require a separate reviewed override.
"""
from datetime import date,timedelta
HOLIDAYS_2026=frozenset(date.fromisoformat(d) for d in (
"2026-01-15","2026-01-26","2026-03-03","2026-03-26",
"2026-03-31","2026-04-03","2026-04-14","2026-05-01",
"2026-05-28","2026-06-26","2026-09-14","2026-10-02",
"2026-10-20","2026-11-10","2026-11-24","2026-12-25"))
SOURCE="NSE/CMTR/71775 (2025-12-12)"
def regular_session(day):
    if day.year!=2026:raise ValueError("No reviewed NSE capital market calendar for this year")
    return day.weekday()<5 and day not in HOLIDAYS_2026
def next_regular_session(asof):
    source=date.fromisoformat(asof)
    if not regular_session(source):raise ValueError("As-of date is not a reviewed regular NSE session")
    d=source+timedelta(days=1)
    for _ in range(10):
        if regular_session(d):return d.isoformat()
        d+=timedelta(days=1)
    raise ValueError("No next session in reviewed calendar")
def check_target(asof,target):
    actual=next_regular_session(asof)
    if target!=actual:raise ValueError(f"Target {target} differs from reviewed next session {actual}")
    return {"asof_date":asof,"target_date":target,"calendar_source":SOURCE,
            "special_sessions_not_covered":True,"approval_state":"RESEARCH_ONLY_NO_TRADING"}

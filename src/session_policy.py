"""Strict session-date controls. Never infer a completed session from wall clock alone."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def validate_dates(asof: str, target: str, now=None):
    previous=date.fromisoformat(asof)
    upcoming=date.fromisoformat(target)
    current=(now or datetime.now(IST)).astimezone(IST)
    if previous >= upcoming:
        raise ValueError("Target session must follow source session")
    if previous > current.date():
        raise ValueError("Future as-of session is not permitted")
    if previous == current.date() and (current.hour,current.minute)<(16,0):
        raise ValueError("Same-day source cannot be considered completed before 16:00 IST")
    if upcoming.weekday()>=5:
        raise ValueError("Target is weekend; verified trading calendar required")
    return {"asof_date":asof,"target_date":target,"date_policy":"BASIC_VALIDATION_ONLY",
            "requires_verified_exchange_calendar":True}

def choose_next_session(asof: str, verified_calendar: list[str]):
    ordered=sorted(set(verified_calendar))
    if ordered!=list(verified_calendar):
        raise ValueError("Trading calendar not strictly ascending and unique")
    next_days=[d for d in ordered if d>asof]
    if not next_days:
        raise ValueError("No verified next session available")
    return next_days[0]

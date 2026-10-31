from datetime import datetime,date,timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from src.dhan_scheduled_pipeline import process_once
from src.scan_store import ScanStore

IST=ZoneInfo("Asia/Kolkata")
REFERENCE_DATES=["2026-10-01","2026-10-05","2026-10-06","2026-10-07","2026-10-08","2026-10-09","2026-10-12","2026-10-13","2026-10-14","2026-10-15","2026-10-16","2026-10-19","2026-10-21","2026-10-22","2026-10-23","2026-10-26","2026-10-27","2026-10-28","2026-10-29","2026-10-30"]
def source(*args,missing_open=False):
    days=[date.fromisoformat(day) for day in REFERENCE_DATES]+[date(2026,11,2)]
    stamps=[]
    for day in days:
        t=datetime(day.year,day.month,day.day,9,15,tzinfo=IST)
        amount=72 if day!=date(2026,11,2) else 6
        stamps.extend(int((t+timedelta(minutes=5*i)).timestamp())
                      for i in range(amount) if not(missing_open and day==date(2026,11,2) and i==0))
    n=len(stamps)
    return {"timestamp":stamps,"open":[100]*n,"high":[101]*n,
            "low":[99]*n,"close":[100]*n,"volume":[1000]*n}

def test_end_to_end_idempotent(tmp_path):
    store=ScanStore("sqlite:///"+str(tmp_path/"scans.db"))
    now=datetime(2026,11,2,9,46,tzinfo=IST)
    run=lambda:process_once("token","2885","RELIANCE",now,store,fetch=source,reference_dates=REFERENCE_DATES)
    first=run()
    assert first["status"]=="SCANNED"
    assert first["historical_sessions"]==20
    assert first["execution_enabled"] is False
    assert run()["status"]=="ALREADY_SCANNED"
    assert store.latest()["setups"][0]["symbol"]=="RELIANCE"

def test_missing_open_never_persists(tmp_path):
    store=ScanStore("sqlite:///"+str(tmp_path/"missing.db"))
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
          store,fetch=lambda *args:source(missing_open=True),reference_dates=REFERENCE_DATES)
    assert result["status"]=="INCOMPLETE_OPENING"

def without_day(day, *, add_older=False):
    payload=source()
    keep=[i for i,t in enumerate(payload["timestamp"])
          if datetime.fromtimestamp(t,IST).date().isoformat()!=day]
    result={key:[values[i] for i in keep] for key,values in payload.items()}
    if add_older:
        older=datetime(2026,9,30,9,15,tzinfo=IST)
        stamps=[int((older+timedelta(minutes=5*i)).timestamp()) for i in range(72)]
        for key in result:
            prefix=stamps if key=="timestamp" else [1000 if key=="volume" else
                    101 if key=="high" else 99 if key=="low" else 100]*72
            result[key]=prefix+result[key]
    return result

def test_missing_recent_session_cannot_be_replaced_by_older_session(tmp_path):
    store=ScanStore("sqlite:///"+str(tmp_path/"missing_day.db"))
    now=datetime(2026,11,2,9,46,tzinfo=IST)
    result=process_once("token","2885","RELIANCE",now,store,
        fetch=lambda *args:without_day("2026-10-29",add_older=True),
        reference_dates=REFERENCE_DATES)
    assert result["status"]=="INCOMPLETE_REFERENCE_HISTORY"
    assert result["missing_dates"]==["2026-10-29"]
    assert not (tmp_path/"missing_day.db").exists()

def test_truncated_reference_day_not_substituted(tmp_path):
    original=source()
    bad_day="2026-10-29"
    keep=[i for i,t in enumerate(original["timestamp"])
          if datetime.fromtimestamp(t,IST).isoformat()!="2026-10-29T10:00:00+05:30"]
    partial={key:[values[i] for i in keep] for key,values in original.items()}
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
        ScanStore("sqlite:///"+str(tmp_path/"partial.db")),fetch=lambda *args:partial,
        reference_dates=REFERENCE_DATES)
    assert result["status"]=="INCOMPLETE_REFERENCE_HISTORY"
    assert bad_day in result["missing_dates"]

def test_calendar_dates_required_before_any_fetch(tmp_path):
    def no_fetch(*args):
        raise AssertionError("Must not fetch without explicit dates")
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
        ScanStore("sqlite:///"+str(tmp_path/"unverified.db")),fetch=no_fetch)
    assert result["status"]=="REFERENCE_DATES_REQUIRED"

def test_future_reference_rejected_before_fetch(tmp_path):
    dates=REFERENCE_DATES[:-1]+["2026-11-02"]
    def no_fetch(*args):
        raise AssertionError("Must not fetch invalid reference dates")
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
        ScanStore("sqlite:///"+str(tmp_path/"future.db")),fetch=no_fetch,reference_dates=dates)
    assert result["status"]=="INVALID_REFERENCE_DATES"

def test_unexpected_session_in_reference_interval_is_held(tmp_path):
    raw=source()
    t=datetime(2026,10,20,9,15,tzinfo=IST)
    extras=[int((t+timedelta(minutes=5*i)).timestamp()) for i in range(72)]
    records=[dict(zip(raw.keys(),values)) for values in zip(*raw.values())]
    records.extend({"timestamp":stamp,"open":100,"high":101,"low":99,"close":100,"volume":1000} for stamp in extras)
    records.sort(key=lambda r:r["timestamp"])
    payload={key:[row[key] for row in records] for key in raw}
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
        ScanStore("sqlite:///"+str(tmp_path/"unexpected.db")),fetch=lambda *args:payload,
        reference_dates=REFERENCE_DATES)
    assert result["status"]=="UNEXPECTED_REFERENCE_SESSION"
    assert result["unexpected_dates"]==["2026-10-20"]

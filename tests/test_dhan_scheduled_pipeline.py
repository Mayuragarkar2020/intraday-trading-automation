from datetime import datetime,date,timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo
from src.dhan_scheduled_pipeline import process_once
from src.scan_store import ScanStore

IST=ZoneInfo("Asia/Kolkata")
def source(*args,missing_open=False):
    start=date(2026,9,29)
    days=[start+timedelta(days=i) for i in range(35) if (start+timedelta(days=i)).weekday()<5]
    days=[d for d in days if d<date(2026,11,2)][-20:]+[date(2026,11,2)]
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
    run=lambda:process_once("token","2885","RELIANCE",now,store,fetch=source)
    first=run()
    assert first["status"]=="SCANNED"
    assert first["historical_sessions"]==20
    assert first["execution_enabled"] is False
    assert run()["status"]=="ALREADY_SCANNED"
    assert store.latest()["setups"][0]["symbol"]=="RELIANCE"

def test_missing_open_never_persists(tmp_path):
    store=ScanStore("sqlite:///"+str(tmp_path/"missing.db"))
    result=process_once("token","2885","RELIANCE",datetime(2026,11,2,9,46,tzinfo=IST),
          store,fetch=lambda *args:source(missing_open=True))
    assert result["status"]=="INCOMPLETE_OPENING"

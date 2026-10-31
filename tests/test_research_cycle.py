import copy
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import pytest
from src.research_cycle import run_cycle
from src.universe_store import UniverseStore

ROOT=Path(__file__).resolve().parents[1]
IST=ZoneInfo("Asia/Kolkata")

@pytest.fixture
def setup(tmp_path):
    report=json.loads((ROOT/"research/2026-10-30/universe.json").read_text(encoding="utf-8"))
    sources=json.loads((ROOT/"research/2026-10-30/nse-eligibility-evidence.json").read_text(encoding="utf-8"))
    store=UniverseStore("sqlite:///"+str(tmp_path/"daily.db"))
    return report,{"nse":sources},store

def clock(hour,minute,day=2):
    return datetime(2026,11,day,hour,minute,tzinfo=IST)

def test_refresh_once_before_market_without_dhan_token(setup):
    report,evidence,store=setup
    calls=[]
    def builder(target):
        calls.append(target)
        return report,evidence
    first=run_cycle(clock(8,30),store,None,None,builder=builder)
    assert first["status"]=="UNIVERSE_REFRESHED"
    second=run_cycle(clock(8,35),store,None,None,builder=builder)
    assert second["status"]=="UNIVERSE_READY"
    assert calls==["2026-11-02"]

def test_market_scan_uses_published_exact_reference_dates(setup):
    report,evidence,store=setup
    run_cycle(clock(8,30),store,None,None,builder=lambda target:(report,evidence))
    calls=[]
    def scanner(token,sid,symbol,now,scan_store,**kwargs):
        calls.append(kwargs["reference_dates"])
        return {"status":"SCANNED","execution_enabled":False}
    result=run_cycle(clock(9,45),store,object(),"not-a-real-token",scanner=scanner)
    assert result["status"]=="SCANNED"
    assert calls==[[r["asof_date"] for r in report["sources"]]]
    assert result["universe_revision"]==store.latest("2026-11-02")["revision"]

def test_missing_refresh_after_open_never_contacts_sources_or_scanner(setup):
    _,_,store=setup
    def forbidden(*args,**kwargs):
        raise AssertionError("No late rebuild or scan without pre-market refresh")
    result=run_cycle(clock(9,45),store,None,"token",builder=forbidden,scanner=forbidden)
    assert result["status"]=="UNIVERSE_REFRESH_MISSING"

def test_failed_build_does_not_publish_or_run_scanner(setup):
    _,_,store=setup
    def failed(target):
        raise ValueError("Missing source")
    with pytest.raises(ValueError,match="Missing source"):
        run_cycle(clock(8,30),store,None,None,builder=failed)
    assert store.latest("2026-11-02") is None

def test_previous_snapshot_not_reused_for_another_day(setup):
    report,evidence,store=setup
    run_cycle(clock(8,30),store,None,None,builder=lambda target:(report,evidence))
    assert run_cycle(clock(9,45,day=3),store,None,"token")["status"]=="UNIVERSE_REFRESH_MISSING"

def test_weekend_exits_before_database_or_source_use():
    class Forbidden:
        def initialize(self):
            raise AssertionError("Weekend must not access store")
    result=run_cycle(datetime(2026,10,31,8,30,tzinfo=IST),Forbidden(),None,None)
    assert result["status"]=="MARKET_CLOSED"

def test_calendar_horizon_failure_keeps_previous_snapshot(setup):
    report,evidence,store=setup
    run_cycle(clock(8,30),store,None,None,builder=lambda target:(report,evidence))
    def builder(target):
        raise ValueError("CALENDAR_REVIEW_REQUIRED")
    with pytest.raises(ValueError,match="CALENDAR_REVIEW_REQUIRED"):
        run_cycle(clock(8,30,day=9),store,None,None,builder=builder)
    assert store.latest("2026-11-02") is not None
    assert store.latest("2026-11-09") is None

def test_advance_publication_is_not_counted_as_today_refresh(setup):
    from datetime import timezone
    report,evidence,store=setup
    store.initialize()
    store.publish(report,evidence,now=datetime(2026,10,31,8,tzinfo=timezone.utc))
    result=run_cycle(clock(9,45),store,None,"token")
    assert result["status"]=="UNIVERSE_REFRESH_MISSING"

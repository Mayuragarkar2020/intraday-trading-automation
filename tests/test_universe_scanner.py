from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime,timedelta
import json
import os
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from src.daily_universe_refresh import reference_dates_for
from src.run_forward_capture import CALENDAR
from src.universe_scanner import UniverseScanStore,run_universe_scan,warm_universe_references


def at(clock="09:45:10",day="2026-11-02"):
    return datetime.fromisoformat(day+"T"+clock+"+05:30")


def data(count=2):
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    report={"mode":"LIQUIDITY_RESEARCH_ONLY","execution_enabled":False,"tradable_count":0,
        "target_date":"2026-11-02","asof_date":dates[-1],
        "sources":[{"asof_date":d,"sha256":"a"*64,"eq_rows":1} for d in dates],
        "candidates":[{"symbol":"STOCK"+str(i),"dhan_security_id":str(100+i),
            "mapping_status":"UNIQUE","liquidity_pass":True,"reference_price_band":"20",
            "reference_review_status":"HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"} for i in range(count)]}
    return {"revision":"b"*64,"created_at":at("08:30:00").isoformat(),"snapshot":report}


class Universe:
    def __init__(self,published): self.published=published
    def latest(self,target): return self.published


def bars(*,history=False,length=72,current_minute=45):
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text())) if history else ["2026-11-02"]
    stamps=[]
    for day in dates:
        first=at("09:15:00",day)
        n=length if history else (current_minute-15)//5
        stamps += [int((first+timedelta(minutes=i*5)).timestamp()) for i in range(n)]
    n=len(stamps)
    return {"timestamp":stamps,"open":[100]*n,"high":[101]*n,
            "low":[99]*n,"close":[100]*n,"volume":[1000]*n}


class Timing:
    def __init__(self,now=None): self.elapsed=0.;self.now=now or at()
    def monotonic(self): return self.elapsed
    def sleep(self,duration): self.elapsed+=duration
    def clock(self): return self.now+timedelta(seconds=self.elapsed+1)


def run(backend,published=None,*,fetch=None,timer=None,now=None,**kwargs):
    now=now or at()
    timer=timer or Timing(now)
    if fetch is None:
        def fetch(token,sid,interval,start,end):
            return bars(history=end=="2026-11-02 09:15:00",current_minute=now.minute)
    return run_universe_scan(now,Universe(published or data()),backend,"fixture-token",fetch=fetch,
            clock=timer.clock,monotonic=timer.monotonic,sleep=timer.sleep,**kwargs)


@pytest.fixture
def backend(tmp_path): return UniverseScanStore("sqlite:///"+str(tmp_path/"scan.db"))


def test_every_eligible_stock_uses_existing_setup_detector(backend):
    report=run(backend)["report"]
    assert report["summary"]=={"SCANNED":2}
    assert report["selected_count"]==2 and report["coverage_complete"]
    assert all(r["setup_status"]=="WAIT" for r in report["rows"])
    assert {r["symbol"] for r in report["rows"]}=={"STOCK0","STOCK1"}
    assert report["broker_requests"]==4
    assert not report["execution_enabled"] and not report["forward_paper_ready"]


def test_real_saved_universe_selects_103_and_retains_all_109_outcomes(backend):
    root=Path(__file__).resolve().parents[1]
    report=json.loads((root/"research/2026-10-30/universe.json").read_text())
    published={"revision":"c"*64,"created_at":at("08:30:00").isoformat(),"snapshot":report}
    result=run(backend,published)["report"]
    assert len(result["rows"])==109
    assert result["selected_count"]==103
    assert result["summary"]=={"SCANNED":103,"HOLD":2,"EXCLUDED":4}
    assert result["coverage_complete"]


def test_low_bands_unknowns_and_identity_holds_never_fetch(backend):
    published=data(4)
    rows=published["snapshot"]["candidates"]
    rows[0]["reference_price_band"]="2"
    rows[1]["reference_price_band"]="5"
    rows[2]["reference_price_band"]=None
    rows[3]["reference_review_status"]="HOLD_NSE_IDENTITY_CONFLICT"
    def forbidden(*args): raise AssertionError("No broker request permitted")
    result=run(backend,published,fetch=forbidden)["report"]
    assert result["broker_requests"]==0
    assert result["summary"]=={"EXCLUDED":2,"HOLD":2}
    assert not result["coverage_complete"]


def test_no_band_is_scanned_as_research_not_labelled_twenty_percent(backend):
    published=data(1);published["snapshot"]["candidates"][0]["reference_price_band"]="No Band"
    assert run(backend,published)["report"]["summary"]=={"SCANNED":1}


def test_history_cached_across_cycles_and_restart(backend):
    run(backend)
    calls=[]
    def fetch(token,sid,interval,start,end):
        calls.append((sid,start,end));return bars(current_minute=50)
    result=run(UniverseScanStore(backend.database_url),fetch=fetch,now=at("09:50:10"))["report"]
    assert result["broker_requests"]==2
    assert all(c[2]=="2026-11-03 09:15:00" for c in calls)
    assert result["coverage_complete"]


def test_premarket_warmup_fetches_only_history_then_setup_scan_uses_cache(backend):
    timer=Timing(at("08:45:10"));calls=[]
    def history_fetch(token,sid,interval,start,end):
        calls.append(end);assert end=="2026-11-02 09:15:00";return bars(history=True)
    warmed=warm_universe_references(timer.now,Universe(data()),backend,"token",fetch=history_fetch,
        clock=timer.clock,monotonic=timer.monotonic,sleep=timer.sleep)["report"]
    assert warmed["mode"]=="REFERENCE_WARMUP_RESEARCH_ONLY"
    assert warmed["summary"]=={"REFERENCE_READY":2}
    assert len(calls)==2
    def current_fetch(token,sid,interval,start,end):
        assert end=="2026-11-03 09:15:00";return bars()
    result=run(backend,fetch=current_fetch)["report"]
    assert result["broker_requests"]==2 and result["coverage_complete"]


def test_same_cycle_retry_does_not_refetch_or_rewrite(backend):
    original=run(backend)["report"]
    def forbidden(*args): raise AssertionError("Already committed cycle")
    retry=run(UniverseScanStore(backend.database_url),fetch=forbidden)
    assert retry["status"]=="ALREADY_SCANNED" and retry["report"]==original


def test_one_bad_stock_does_not_block_other_stocks(backend):
    def fetch(token,sid,interval,start,end):
        raw=bars(history=end=="2026-11-02 09:15:00")
        if sid=="100": raw["low"][0]=200
        return raw
    result=run(backend,fetch=fetch)["report"]
    assert result["summary"]=={"HOLD":1,"SCANNED":1}
    assert not result["coverage_complete"]


@pytest.mark.parametrize("status,reason",[(401,"BROKER_AUTH_HOLD"),(403,"BROKER_AUTH_HOLD"),(429,"BROKER_RATE_LIMIT_HOLD")])
def test_auth_and_rate_limits_stop_remaining_broker_requests(backend,status,reason):
    calls=[]
    def fetch(*args):
        calls.append(args)
        response=httpx.Response(status,request=httpx.Request("POST","https://fixture.invalid"))
        raise httpx.HTTPStatusError("private fixture-token response",request=response.request,response=response)
    report=run(backend,fetch=fetch)["report"]
    assert len(calls)==1
    assert all(r["reason"]==reason for r in report["rows"])
    assert "fixture-token" not in json.dumps(report)


def test_budget_holds_unscanned_stocks_and_keeps_history_cache(backend):
    timer=Timing()
    def fetch(*args): timer.elapsed+=3;return bars(history=True)
    report=run(backend,fetch=fetch,timer=timer,budget_seconds=2)["report"]
    assert report["broker_requests"]==1
    assert all(r["reason"]=="CYCLE_BUDGET_EXHAUSTED" for r in report["rows"])
    assert backend.reference("b"*64,"100") is not None


def test_requests_are_spaced_with_headroom(backend):
    timer=Timing();times=[]
    def fetch(token,sid,interval,start,end):
        times.append(timer.elapsed);return bars(history=end=="2026-11-02 09:15:00")
    run(backend,fetch=fetch,timer=timer)
    assert all(b-a>=.3-1e-9 for a,b in zip(times,times[1:]))


@pytest.mark.parametrize("length",[72,75])
def test_both_regular_reference_shapes_supported_as_research_only(backend,length):
    def fetch(token,sid,interval,start,end):
        return bars(history=end=="2026-11-02 09:15:00",length=length)
    report=run(backend,fetch=fetch)["report"]
    assert report["coverage_complete"] and not report["session_classification_verified"]


@pytest.mark.parametrize("change",["missing_slot","missing_day","unexpected_day"])
def test_reference_gaps_or_extra_sessions_fail_without_substitution(backend,change):
    def fetch(token,sid,interval,start,end):
        raw=bars(history=True)
        if change=="unexpected_day":
            extra=int(at("09:15:00","2026-10-20").timestamp())
            rows=[dict(zip(raw,values)) for values in zip(*raw.values())]
            rows.append({"timestamp":extra,"open":100,"high":101,"low":99,"close":100,"volume":1000})
            rows.sort(key=lambda r:r["timestamp"])
            return {k:[r[k] for r in rows] for k in raw}
        n=1 if change=="missing_slot" else 72
        return {k:v[n:] for k,v in raw.items()}
    assert run(backend,fetch=fetch)["report"]["summary"]=={"HOLD":2}


def test_missing_latest_candle_or_stale_receipt_is_not_scanned(backend):
    def fetch(token,sid,interval,start,end):
        return bars(history=end=="2026-11-02 09:15:00",current_minute=40)
    assert run(backend,fetch=fetch)["report"]["summary"]=={"HOLD":2}


def test_invalid_volume_baseline_is_a_hold_not_complete_coverage(backend):
    def fetch(token,sid,interval,start,end):
        history=end=="2026-11-02 09:15:00"
        raw=bars(history=history)
        if history: raw["volume"]=[0]*len(raw["volume"])
        return raw
    report=run(backend,fetch=fetch)["report"]
    assert report["summary"]=={"HOLD":2} and not report["coverage_complete"]


def test_duplicate_security_ids_hold_both_symbols(backend):
    published=data();published["snapshot"]["candidates"][1]["dhan_security_id"]="100"
    def forbidden(*args): raise AssertionError("Duplicate mapping")
    assert run(backend,published,fetch=forbidden)["report"]["broker_requests"]==0


@pytest.mark.parametrize("now",[at("08:45:00"),at("11:31:00"),at(day="2026-11-07")])
def test_inactive_clock_gates_do_not_touch_sources_or_database(now):
    class Forbidden:
        def latest(self,*args): raise AssertionError("No universe read")
        def initialize(self): raise AssertionError("No DB write")
    result=run_universe_scan(now,Forbidden(),Forbidden(),"token")
    assert result["status"] in {"OUTSIDE_SETUP_WINDOW","UNREVIEWED_SESSION"}


@pytest.mark.parametrize("change",["old_publication","future_publication","no_revision"])
def test_same_day_publication_required_before_scan_store_access(change):
    published=data()
    if change=="old_publication": published["created_at"]=at("08:30:00","2026-11-01").isoformat()
    elif change=="future_publication": published["created_at"]=at("10:00:00").isoformat()
    else: published["revision"]=""
    assert run_universe_scan(at(),Universe(published),None,"token")["status"]=="SAME_DAY_UNIVERSE_REQUIRED"


def test_cache_corruption_holds_stock_without_refetching_history(backend):
    run(backend)
    with backend.connection() as db:
        db.execute("UPDATE universe_scan_reference_cache SET sha256=? WHERE security_id=?",("0"*64,"100"))
    result=run(backend,now=at("09:50:10"))["report"]
    assert result["summary"]=={"HOLD":1,"SCANNED":1}


def test_database_failure_propagates_not_success(tmp_path):
    backend=UniverseScanStore("sqlite:///"+str(tmp_path/"missing"/"scan.db"))
    with pytest.raises(Exception): run(backend)


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"),reason="PostgreSQL CI only")
def test_postgres_concurrent_cycle_commit_and_cache():
    backend=UniverseScanStore(os.environ["TEST_UNIVERSE_DATABASE_URL"])
    published=data(1);published["revision"]=uuid4().hex+uuid4().hex
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(lambda _:run(backend,published),range(3)))
    assert sum(r["status"]=="SCANNED" for r in results)==1
    assert all(r["report"]==results[0]["report"] for r in results)


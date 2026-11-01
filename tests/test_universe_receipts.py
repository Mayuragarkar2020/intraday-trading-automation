from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
import os
from uuid import uuid4

import pytest

from src.universe_receipts import UniverseReceiptStore, canonical_candidate, digest
from src.universe_scanner import UniverseScanStore, candidate_from, prepare_history
from src.daily_universe_refresh import reference_dates_for
from src.run_forward_capture import CALENDAR
import json
from tests.test_universe_scanner import at, bars, run, data


def candidate(minute=45):
    now=at(f"09:{minute:02}:10")
    raw=bars(current_minute=minute)
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    previous=prepare_history(bars(history=True),now,dates)
    return candidate_from("STOCK0",previous,raw,now,now.replace(second=0)),raw,now


@pytest.fixture
def backend(tmp_path):
    url="sqlite:///"+str(tmp_path/"receipts.db")
    scan=UniverseScanStore(url);scan.initialize()
    scan.save_reference("b"*64,"100",bars(history=True))
    return UniverseReceiptStore(url)


def record(backend,minute=45,*,value=None,clock=None):
    c,raw,now=candidate(minute)
    return backend.record("b"*64,"100",value or c,digest(bars(history=True)),digest(raw),
                          now.isoformat(),clock=clock or (lambda:now+timedelta(seconds=1)))


def test_initial_backfill_is_held_then_last_three_receipts_become_timely(backend):
    first=record(backend)["receipt"]
    assert first["receipt_status"]=="HELD_SETUP_FIRST_SEEN"
    record(backend,50)
    third=record(backend,55)["receipt"]
    assert third["receipt_status"]=="TIMELY_RESEARCH_EVIDENCE"
    assert third["known_at"].endswith("09:55:11+05:30")
    assert not third["forward_paper_ready"] and not third["execution_enabled"]
    assert not any(third[k] for k in ("timestamp_verified","session_contract_verified",
                                    "reference_prices_verified","breakout_receipts_verified"))
    assert backend.read(third["receipt_id"])==third


def test_retry_preserves_first_known_time_after_restart(backend):
    first=record(backend)["receipt"]
    result=record(UniverseReceiptStore(backend.database_url),clock=lambda:at("10:00:00"))
    assert result=={"status":"ALREADY_RECORDED","receipt":first}


def test_economic_decimal_spelling_does_not_revise_candles(backend):
    first=record(backend)["receipt"]
    c,raw,now=candidate()
    from decimal import Decimal
    c.completed_5m[0].close=Decimal("100.000")
    assert record(backend,value=c)["receipt"]==first


def test_new_candle_revision_rolls_back_entire_observation(backend):
    record(backend)
    c,_,_=candidate(50);c.completed_5m[0].close="100.5"
    # Rebuild candidate from modified current input to avoid failing only the
    # indicator-input binding gate. A past candle itself must remain immutable.
    raw=bars(current_minute=50);raw["close"][0]=100.5
    now=at("09:50:10")
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    previous=prepare_history(bars(history=True),now,dates)
    c=candidate_from("STOCK0",previous,raw,now,now.replace(second=0))
    with pytest.raises(ValueError,match="revision"):
        backend.record("b"*64,"100",c,digest(bars(history=True)),digest(raw),now.isoformat(),clock=lambda:now)
    with backend.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM universe_receipt_signals").fetchone()[0]==1
        assert db.execute("SELECT COUNT(*) FROM universe_receipt_candles").fetchone()[0]==6


@pytest.mark.parametrize("field",["completed_15m","ema_warmup_closes","previous_sessions"])
def test_injected_indicators_or_reference_prices_are_rejected(backend,field):
    c,_,_=candidate()
    from decimal import Decimal
    if field=="completed_15m": c.completed_15m[-1].close=Decimal("100.5")
    elif field=="ema_warmup_closes": c.ema_warmup_closes[-1]=Decimal("100.5")
    else: c.previous_sessions[0][0].close=Decimal("100.5")
    with pytest.raises(ValueError,match="retained source"):
        record(backend,value=c)


@pytest.mark.parametrize("clock",[lambda:at("09:45:09"),lambda:at("09:47:00"),
                                  lambda:at().replace(tzinfo=None)])
def test_invalid_post_scan_clock_rolls_back_candles(backend,clock):
    with pytest.raises(ValueError): record(backend,clock=clock)
    with backend.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM universe_receipt_candles").fetchone()[0]==0


def test_concurrent_writers_share_one_immutable_receipt(backend):
    backend.initialize()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:record(backend),range(4)))
    assert sum(r["status"]=="RECORDED" for r in results)==1


def test_receipt_corruption_is_detected(backend):
    receipt=record(backend)["receipt"]
    with backend.connection() as db:
        db.execute("UPDATE universe_receipt_signals SET sha256='broken'")
    with pytest.raises(ValueError,match="integrity"): backend.read(receipt["receipt_id"])


@pytest.mark.parametrize("target",["cache","candle","first_seen"])
def test_retained_source_corruption_is_detected_on_read(backend,target):
    receipt=record(backend)["receipt"]
    with backend.connection() as db:
        if target=="cache": db.execute("UPDATE universe_scan_reference_cache SET payload='{}'")
        elif target=="candle": db.execute("UPDATE universe_receipt_candles SET payload='{}'")
        else: db.execute("UPDATE universe_receipt_candles SET first_seen_at='2026-11-02T10:00:00+05:30'")
    with pytest.raises(ValueError,match="integrity"): backend.read(receipt["receipt_id"])


def test_conflicting_same_close_input_cannot_rewrite_signal(backend):
    record(backend)
    c,raw,now=candidate()
    raw["close"][-1]=100.5
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    c=candidate_from("STOCK0",prepare_history(bars(history=True),now,dates),raw,now,now.replace(second=0))
    with pytest.raises(ValueError,match="conflict"):
        record(backend,value=c)


def test_second_observation_failure_rolls_back_new_candles_and_receipt(backend):
    record(backend)
    with backend.connection() as db:
        db.execute("""CREATE TRIGGER fail_receipt BEFORE INSERT ON universe_receipt_signals
                      BEGIN SELECT RAISE(ABORT,'injected receipt failure'); END""")
    with pytest.raises(Exception,match="injected receipt failure"): record(backend,50)
    with backend.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM universe_receipt_signals").fetchone()[0]==1
        assert db.execute("SELECT COUNT(*) FROM universe_receipt_candles").fetchone()[0]==6


def test_opt_in_full_pool_records_without_enabling_trading(tmp_path):
    url="sqlite:///"+str(tmp_path/"integrated.db")
    scan=UniverseScanStore(url)
    result=run(scan,receipt_store=UniverseReceiptStore(url))["report"]
    assert result["receipt_evidence_enabled"]
    assert result["receipt_summary"]=={"HELD_SETUP_FIRST_SEEN":2}
    assert all(r.get("receipt_id") for r in result["rows"])
    assert result["coverage_complete"] and not result["forward_paper_ready"]


def test_default_scanner_does_not_create_receipt_tables(tmp_path):
    url="sqlite:///"+str(tmp_path/"disabled.db")
    scan=UniverseScanStore(url)
    assert not run(scan)["report"]["receipt_evidence_enabled"]
    with scan.connection() as db:
        assert not db.execute("SELECT name FROM sqlite_master WHERE name LIKE 'universe_receipt_%'").fetchall()


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"),reason="PostgreSQL CI only")
def test_postgres_receipt_concurrency_restart():
    from urllib.parse import urlencode
    import psycopg
    from psycopg import sql
    url=os.environ["TEST_UNIVERSE_DATABASE_URL"]
    schema="receipts_"+uuid4().hex
    with psycopg.connect(url) as db:
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    scoped=url+("&" if "?" in url else "?")+urlencode({"options":"-csearch_path="+schema})
    try:
        scan=UniverseScanStore(scoped);scan.initialize()
        scan.save_reference("b"*64,"100",bars(history=True))
        backend=UniverseReceiptStore(scoped);backend.initialize()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _:record(backend),range(4)))
        assert sum(r["status"]=="RECORDED" for r in results)==1
        assert record(UniverseReceiptStore(scoped))["status"]=="ALREADY_RECORDED"
    finally:
        with psycopg.connect(url) as db:
            db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))

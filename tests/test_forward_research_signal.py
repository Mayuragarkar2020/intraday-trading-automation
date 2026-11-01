from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import hashlib
import json
import os
from urllib.parse import urlencode
from uuid import uuid4

import pytest

from src.daily_universe_refresh import reference_dates_for
from src.forward_capture import ForwardCaptureStore, prepare_capture
from src.forward_research_signal import ForwardResearchSignalStore
from src.run_forward_capture import CALENDAR
from src.universe_store import UniverseStore


def at(clock="09:45:10"):
    return datetime.fromisoformat("2026-11-02T"+clock+"+05:30")


def dataset():
    dates = reference_dates_for("2026-11-02", json.loads(CALENDAR.read_text()))
    previous = []
    for day in dates:
        first = datetime.fromisoformat(day+"T09:20:00+05:30")
        previous.append([{"time": (first+timedelta(minutes=i*5)).isoformat(),
            "open": "100", "high": "101", "low": "99", "close": "100", "volume": 1000}
            for i in range(72)])
    raw = {"timestamp": [int(at("09:15:00").timestamp())+i*300 for i in range(6)],
           "open": [100]*6, "high": [101]*6, "low": [99]*6,
           "close": [100]*6, "volume": [1000]*6}
    snapshot = {"mode": "LIQUIDITY_RESEARCH_ONLY", "execution_enabled": False,
        "tradable_count": 0, "restrictions_verified": False,
        "calendar_completeness_verified": False, "target_date": "2026-11-02",
        "asof_date": dates[-1],
        "sources": [{"asof_date": d, "sha256": "a"*64, "eq_rows": 1} for d in dates],
        "candidates": [{"symbol": "RELIANCE", "dhan_security_id": "2885",
            "reference_review_status": "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE",
            "liquidity_pass": True, "mapping_status": "UNIQUE"}]}
    return previous, raw, snapshot


def seed(url, *, reconnect=False):
    previous, raw, snapshot = dataset()
    # Deliberate synthetic DB fixtures. These are never production source evidence.
    universe = UniverseStore(url)
    universe.initialize()
    payload = json.dumps(snapshot,sort_keys=True,separators=(",", ":"))
    proof = '{"fixture":true}'
    revision = hashlib.sha256((payload+"\n"+proof).encode()).hexdigest()
    backend = ForwardCaptureStore(url)
    p = "%s" if backend.postgres else "?"
    with backend.connection() as db:
        db.execute("INSERT INTO universe_research_snapshots VALUES ("+",".join([p]*6)+") "
                   "ON CONFLICT DO NOTHING", (revision,"2026-11-02",snapshot["asof_date"],
                   at("08:30:00").isoformat(),payload,proof))
    clocks = ["09:45:10"] if reconnect else [f"09:{m:02}:10" for m in (20,25,30,35,40,45)]
    for clock in clocks:
        backend.save(prepare_capture(raw,at(clock),revision))
    return ForwardResearchSignalStore(url), previous


@pytest.fixture
def inputs(tmp_path):
    return seed("sqlite:///"+str(tmp_path/"signals.db"))


def record(backend, previous, clock=at("09:45:20")):
    return backend.record(at().isoformat(), previous, clock=lambda:clock)


def test_receipt_bound_signal_keeps_exact_inputs_and_never_clears_execution(inputs):
    backend, previous = inputs
    result = record(backend,previous)
    signal = result["signal"]
    assert result["status"] == "RECORDED"
    assert signal["known_at"] == at("09:45:20").isoformat()
    assert signal["observed_at"] == at().isoformat()
    assert signal["scanner_result"]["status"] == "WAIT"
    assert signal["mode"] == "RECEIPT_BOUND_RESEARCH_ONLY"
    assert not signal["forward_paper_ready"] and not signal["execution_enabled"]
    assert not signal["reference_prices_verified"] and not signal["session_contract_verified"]
    assert len(signal["candidate"]["completed_5m"]) == 6
    assert len(signal["candidate"]["previous_sessions"]) == 20
    assert signal["first_seen"][-1]["first_observed_at"] == at().isoformat()


def test_retry_keeps_original_known_at_after_restart(inputs):
    backend, previous = inputs
    first = record(backend,previous)["signal"]
    retry = record(ForwardResearchSignalStore(backend.database_url),previous,at("10:00:00"))
    assert retry == {"status": "ALREADY_RECORDED", "signal": first}


def test_concurrent_workers_journal_one_signal(inputs):
    backend, previous = inputs
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: record(backend,previous),range(4)))
    assert sum(r["status"] == "RECORDED" for r in results) == 1


def test_changed_reference_prices_cannot_rewrite_a_signal(inputs):
    backend, previous = inputs
    record(backend,previous)
    previous[0][0]["close"] = "100.5"
    with pytest.raises(ValueError,match="input conflict"):
        record(backend,previous)


@pytest.mark.parametrize("clock", [at("09:45:09"),at("09:47:00"),datetime(2026,11,2,9,45,20)])
def test_post_scan_clock_must_be_aware_fresh_and_not_backdated(inputs,clock):
    backend, previous = inputs
    with pytest.raises(ValueError):
        record(backend,previous,clock)
    with backend.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM forward_research_signals").fetchone()[0] == 0


def test_no_uncommitted_or_uploaded_current_data_can_be_supplied(inputs):
    backend, previous = inputs
    with pytest.raises(ValueError,match="Committed"):
        backend.record(at("09:46:00").isoformat(),previous)
    with pytest.raises(TypeError):
        backend.record(at().isoformat(),previous,current_candles=[])


def test_reconnect_batch_cannot_become_timely_signal(tmp_path):
    backend, previous = seed("sqlite:///"+str(tmp_path/"reconnect.db"),reconnect=True)
    with pytest.raises(ValueError,match="late first-seen"):
        record(backend,previous)


@pytest.mark.parametrize("change", ["missing_reference", "wrong_date", "bad_ohlc", "extra_reference"])
def test_reference_shape_and_dates_fail_closed(inputs,change):
    backend, previous = inputs
    if change == "missing_reference": previous[1].pop()
    elif change == "wrong_date": previous[0] = previous[1]
    elif change == "bad_ohlc": previous[0][0]["high"] = "98"
    else: previous.append(previous[-1])
    with pytest.raises(ValueError):
        record(backend,previous)


@pytest.mark.parametrize("target", ["capture_hash", "candle", "universe_hash", "first_seen"])
def test_stored_identity_corruption_is_detected(inputs,target):
    backend, previous = inputs
    with backend.connection() as db:
        if target == "capture_hash":
            rows = db.execute("SELECT payload FROM forward_research_observations WHERE observed_at=?",(at().isoformat(),)).fetchone()
            report = json.loads(rows[0]); report["source_sha256"] = "0"*64
            db.execute("UPDATE forward_research_observations SET payload=? WHERE observed_at=?",(json.dumps(report),at().isoformat()))
        elif target == "candle":
            db.execute("UPDATE forward_research_candles SET payload='{}'")
        elif target == "universe_hash":
            db.execute("UPDATE universe_research_snapshots SET evidence='{}'")
        else:
            db.execute("UPDATE forward_research_candles SET first_observed_at=?",(at("09:46:00").isoformat(),))
    with pytest.raises(ValueError):
        record(backend,previous)


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"),reason="PostgreSQL CI only")
def test_postgres_concurrent_signal_binding():
    import psycopg
    from psycopg import sql
    url = os.environ["TEST_UNIVERSE_DATABASE_URL"]
    schema = "signal_fixture_"+uuid4().hex
    with psycopg.connect(url) as db:
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    scoped = url+("&" if "?" in url else "?")+urlencode({"options":"-csearch_path="+schema})
    try:
        backend, previous = seed(scoped)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _:record(backend,previous),range(4)))
        assert sum(r["status"] == "RECORDED" for r in results) == 1
    finally:
        with psycopg.connect(url) as db:
            db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


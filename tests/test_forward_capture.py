from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os

import pytest

from src.forward_capture import ForwardCaptureStore, prepare_capture
from src.run_forward_capture import capture_once, main


def at(clock="09:30:10", day="2026-11-02"):
    return datetime.fromisoformat(day+"T"+clock+"+05:30")


def candles(minutes=(15,20,25)):
    return {"timestamp": [int(at("09:%02d:00" % m).timestamp()) for m in minutes],
            "open": ["100"]*len(minutes), "high": ["102"]*len(minutes),
            "low": ["99"]*len(minutes), "close": ["101"]*len(minutes),
            "volume": [1000]*len(minutes)}


def store(tmp_path):
    return ForwardCaptureStore("sqlite:///"+str(tmp_path/"capture.db"))


def test_first_seen_is_not_backdated_and_restart_is_idempotent(tmp_path):
    backend = store(tmp_path)
    report = prepare_capture(candles(), at(), "reference-revision")
    first = backend.save(report)
    assert first["status"] == "CAPTURED"
    assert first["report"]["new_candles"] == 3
    assert len(first["report"]["late_first_observations"]) == 2
    assert first["report"]["observed_at"] == at().isoformat()
    again = store(tmp_path).save(report)
    assert again["status"] == "ALREADY_CAPTURED"
    assert again["report"] == first["report"]
    assert not again["report"]["execution_enabled"]
    assert not again["report"]["forward_paper_ready"]


def test_duplicate_tick_and_concurrent_writers_cannot_duplicate_candles(tmp_path):
    report = prepare_capture(candles(), at(), "r")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store(tmp_path).save(report), range(4)))
    assert sum(r["status"] == "CAPTURED" for r in results) == 1
    with store(tmp_path).connection() as db:
        assert db.execute("SELECT COUNT(*) FROM forward_research_candles").fetchone()[0] == 3


def test_revised_candle_rolls_back_whole_batch_and_retains_original(tmp_path):
    backend = store(tmp_path)
    backend.save(prepare_capture(candles(), at(), "r"))
    revised = candles((15,20,25,30))
    revised["close"][1] = "100.50"
    with pytest.raises(ValueError, match="revision"):
        backend.save(prepare_capture(revised, at("09:35:10"), "r"))
    with backend.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM forward_research_candles").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM forward_research_observations").fetchone()[0] == 1
    assert backend.latest()["source_sha256"] == prepare_capture(candles(), at(), "r")["source_sha256"]


def test_same_observation_clock_with_different_reference_is_rejected(tmp_path):
    backend = store(tmp_path)
    backend.save(prepare_capture(candles(), at(), "r"))
    with pytest.raises(ValueError, match="identity"):
        backend.save(prepare_capture(candles(), at(), "changed"))


def test_equivalent_decimal_encoding_is_not_a_price_revision(tmp_path):
    backend = store(tmp_path)
    first = prepare_capture(candles(), at(), "r")
    backend.save(first)
    different_encoding = candles()
    for field in ("open", "high", "low", "close"):
        different_encoding[field] = [float(x) for x in different_encoding[field]]
    second = prepare_capture(different_encoding, at("09:30:20"), "r")
    assert second["source_sha256"] == first["source_sha256"]
    assert backend.save(second)["report"]["new_candles"] == 0


def test_stale_missing_future_and_reconnect_are_explicit(tmp_path):
    assert prepare_capture(candles((15,20)), at(), "r")["status"] == "INCOMPLETE_SESSION"
    assert prepare_capture(candles((20,25)), at(), "r")["missing_closes"] == [at("09:20:00").isoformat()]
    assert prepare_capture(candles(), at("09:32:00"), "r")["status"] == "STALE"
    assert len(prepare_capture(candles((15,20,25,30)), at(), "r")["candles"]) == 3
    backend = store(tmp_path)
    backend.save(prepare_capture(candles((15,)), at("09:20:10"), "r"))
    result = backend.save(prepare_capture(candles(), at("09:32:00"), "r"))
    assert result["report"]["new_candles"] == 2
    assert len(result["report"]["late_first_observations"]) == 2
    assert not result["report"]["backfilled_candles_are_trade_events"]


@pytest.mark.parametrize("now", [at("09:19:00"), at("15:26:00"),
    at(day="2026-11-01"), datetime(2026,11,2,9,30)])
def test_clock_gates(now):
    with pytest.raises(ValueError):
        prepare_capture(candles(), now, "r")


def test_duplicate_raw_candles_fail_before_storage():
    with pytest.raises(ValueError):
        prepare_capture(candles((15,15,20)), at(), "r")


def test_post_cutoff_never_invents_extra_continuous_candles():
    payload = candles((15,))
    result = prepare_capture(payload, at("15:20:00"), "r")
    assert result["expected_close"] == at("15:15:00").isoformat()
    assert all(t <= at("15:15:00").isoformat() for t in result["missing_closes"])


class Universe:
    def __init__(self, value): self.value = value
    def latest(self, target): return self.value


def reference():
    from src.daily_universe_refresh import reference_dates_for
    from src.run_forward_capture import CALENDAR
    dates = reference_dates_for("2026-11-02", json.loads(CALENDAR.read_text()))
    report = {"mode": "LIQUIDITY_RESEARCH_ONLY", "execution_enabled": False,
              "tradable_count": 0, "target_date": "2026-11-02", "asof_date": dates[-1],
              "sources": [{"asof_date": d, "sha256": "a"*64, "eq_rows": 1} for d in dates],
              "candidates": [{"symbol": "RELIANCE", "dhan_security_id": "2885",
                "reference_review_status": "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE",
                "liquidity_pass": True, "mapping_status": "UNIQUE"}]}
    return {"snapshot": report, "revision": "r", "created_at": at("08:30:00").isoformat()}


def test_runner_binds_same_day_reference_and_fetch_received_clock(tmp_path):
    calls = []
    def fetch(*args):
        calls.append(args)
        return candles()
    result = capture_once(at(), Universe(reference()), store(tmp_path), "secret",
                          fetch=fetch, clock=lambda: at("09:30:45"))
    assert result["report"]["observed_at"] == at("09:30:45").isoformat()
    assert result["report"]["universe_revision"] == "r"
    assert calls[0][1:3] == ("2885", 5)


@pytest.mark.parametrize("kind,expected", [("old_publication", "SAME_DAY_UNIVERSE_REQUIRED"),
    ("missing", "SAME_DAY_UNIVERSE_REQUIRED"), ("held", "UNIVERSE_SYMBOL_HELD_OR_EXCLUDED"),
    ("token", "DHAN_TOKEN_NOT_CONFIGURED"), ("outside", "OUTSIDE_CAPTURE_WINDOW"),
    ("unreviewed", "UNREVIEWED_CAPTURE_DATE")])
def test_runner_gates_before_broker_or_capture_store(kind, expected):
    value = reference()
    now, token = at(), "secret"
    if kind == "old_publication": value["created_at"] = at(day="2026-11-01").isoformat()
    elif kind == "missing": value = None
    elif kind == "held": value["snapshot"]["candidates"][0]["reference_review_status"] = "EXCLUDED_NSE_ASM"
    elif kind == "token": token = None
    elif kind == "outside": now = at("08:30:00")
    elif kind == "unreviewed": now = at(day="2026-11-09")
    def forbidden(*args): raise AssertionError("Must not fetch")
    assert capture_once(now, Universe(value), None, token, fetch=forbidden)["status"] == expected


def test_capture_clock_after_fetch_cannot_be_backdated(tmp_path):
    with pytest.raises(ValueError, match="clock"):
        capture_once(at(), Universe(reference()), store(tmp_path), "secret",
                     fetch=lambda *args: candles(), clock=lambda: at("09:30:00"))


def test_default_disabled_never_touches_store_or_broker(monkeypatch, capsys):
    monkeypatch.delenv("FORWARD_CAPTURE_ENABLED", raising=False)
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["status"] == "FORWARD_CAPTURE_DISABLED"


def test_reference_dates_must_match_reviewed_calendar_before_fetch():
    value = reference()
    value["snapshot"]["sources"][0]["asof_date"] = "2026-09-30"
    def forbidden(*args): raise AssertionError("Must not fetch")
    result = capture_once(at(), Universe(value), None, "secret", fetch=forbidden)
    assert result["status"] == "CAPTURE_REFERENCE_DATES_MISMATCH"


def test_scheduled_runner_preserves_default_window_and_opt_in_capture(monkeypatch, capsys):
    import src.run_scheduled_research as scheduled
    import src.run_forward_capture as recorder
    calls = []
    monkeypatch.setenv("SCAN_DATABASE_URL", "postgresql://test-only")
    monkeypatch.delenv("FORWARD_CAPTURE_ENABLED", raising=False)
    def window(now, **kwargs):
        calls.append(kwargs["end"].isoformat())
        return True, "ACTIVE"
    monkeypatch.setattr(scheduled, "research_window", window)
    monkeypatch.setattr(scheduled, "run_cycle", lambda *args: {"status": "RESEARCH_ONLY"})
    def capture(*args):
        calls.append("CAPTURE")
        return {"status": "CAPTURED", "report": {"status": "FRESH_OBSERVATION"}}
    monkeypatch.setattr(recorder, "capture_once", capture)
    assert scheduled.main() == 0
    assert calls == ["11:40:00"]
    monkeypatch.setenv("FORWARD_CAPTURE_ENABLED", "true")
    assert scheduled.main() == 0
    assert calls == ["11:40:00", "15:25:00", "CAPTURE"]
    assert "test-only" not in capsys.readouterr().out


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"), reason="PostgreSQL CI only")
def test_postgres_concurrent_capture_and_restart():
    backend = ForwardCaptureStore(os.environ["TEST_UNIVERSE_DATABASE_URL"])
    backend.initialize()
    report = prepare_capture(candles(), at(), "pg-reference")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: backend.save(report), range(4)))
    assert sum(r["status"] == "CAPTURED" for r in results) == 1
    assert backend.save(report)["status"] == "ALREADY_CAPTURED"

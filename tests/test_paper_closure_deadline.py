"""Completed closure, failed/partial exits and recovery use distinct evidence."""
from datetime import datetime, timedelta

import pytest

from src.paper_engine import replay
from src.paper_models import ReplayRequest
from src.paper_scenarios import example_request


def day():
    data = example_request()
    data.update(slippage_bps="0", round_trip_cost_per_share="0")
    plan = data["plans"][0]
    start = datetime.fromisoformat(plan["known_at"])
    plan["bars"] = [dict(time=(start+timedelta(minutes=i*5)).isoformat(),
        open=500, high=501, low=499, close=500, ema10=499, volume=1000000)
        for i in range(1, 67)]  # through 15:15 close
    return data


def run(data):
    return replay(ReplayRequest.model_validate(data),
                  as_of=datetime.fromisoformat("2026-10-31T12:00:00+05:30"))


def test_default_deadline_and_early_exit_are_explicit():
    result = run(day())
    assert result["assumptions"]["force_exit"] == "15:00"
    assert result["assumptions"]["flatten_request_at"] == "14:50"
    trade = result["trades"][0]
    assert trade["exit_fill_at"].endswith("14:50:00+05:30")
    assert trade["exit_reason"] == "SESSION_FLATTEN"
    assert not result["summary"]["closure_deadline_breached"]


@pytest.mark.parametrize("fault", ["reject_exit", "can_fill", "volume"])
def test_failed_first_attempt_retries_before_deadline(fault):
    data = day()
    bar = next(b for b in data["plans"][0]["bars"] if "14:55:" in b["time"])
    bar[fault] = {"reject_exit":True,"can_fill":False,"volume":0}[fault]
    result = run(data)
    assert any(e["kind"] == "EXIT_UNFILLED" for e in result["events"])
    assert result["trades"][0]["exit_fill_at"].endswith("14:55:00+05:30")
    assert not result["summary"]["closure_deadline_breached"]


def test_partial_exit_keeps_exposure_and_deadline_breach():
    data = day()
    for bar in data["plans"][0]["bars"]:
        if bar["time"][11:16] >= "14:55":
            bar["volume"] = 100
    result = run(data)
    assert result["open_position"]["remaining"] > 0
    assert result["summary"]["closure_deadline_breached"]
    assert not result["summary"]["complete"]


def test_late_recovery_remains_a_deadline_breach():
    data = day()
    for bar in data["plans"][0]["bars"]:
        if "14:55" <= bar["time"][11:16] <= "15:05":
            bar["reject_exit"] = True
    result = run(data)
    assert result["summary"]["complete"]
    assert result["trades"][0]["exit_fill_at"].endswith("15:05:00+05:30")
    assert result["summary"]["closure_deadline_breached"]


def test_missing_executable_tail_does_not_manufacture_closure():
    data = day()
    data["plans"][0]["bars"] = data["plans"][0]["bars"][:-5]
    result = run(data)
    assert result["summary"]["open_positions"] == 1
    assert result["summary"]["closure_deadline_breached"]
    assert not result["trades"]


def test_old_late_deadline_is_rejected_and_version_changes_run_identity():
    data = day()
    data["force_exit"] = "15:15"
    with pytest.raises(ValueError, match="15:00"):
        run(data)
    assert run(day())["engine_version"] == "paper-replay-2-deadline"

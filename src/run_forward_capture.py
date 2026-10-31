"""Opt-in finite RELIANCE research recorder, independent of paper execution."""
import json
import os
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.dhan_history_client import fetch_intraday
from src.forward_capture import ForwardCaptureStore, prepare_capture
from src.universe_store import UniverseStore

IST = ZoneInfo("Asia/Kolkata")
CALENDAR = Path(__file__).resolve().parents[1] / "config/research_calendar.json"


def capture_once(now, universe_store, capture_store, token, *, fetch=fetch_intraday,
                 calendar_path=CALENDAR, clock=lambda: datetime.now(IST)):
    if now.tzinfo is None:
        raise ValueError("Aware clock required")
    local = now.astimezone(IST)
    target = local.date().isoformat()
    calendar = json.loads(Path(calendar_path).read_text())
    if (target not in calendar["sessions"] or
            not calendar["earliest_target"] <= target <= calendar["latest_target"]):
        return {"status": "UNREVIEWED_CAPTURE_DATE", "execution_enabled": False}
    from src.daily_universe_refresh import reference_dates_for
    expected_dates = reference_dates_for(target, calendar)
    if local.weekday() >= 5 or not time(9,20) <= local.time() <= time(15,25):
        return {"status": "OUTSIDE_CAPTURE_WINDOW", "execution_enabled": False}
    if not token:
        return {"status": "DHAN_TOKEN_NOT_CONFIGURED", "execution_enabled": False}
    # Reading the same-day published reference is required before broker/storage access.
    current = universe_store.latest(target)
    if (not current or current["snapshot"]["target_date"] != target or
            datetime.fromisoformat(current["created_at"]).astimezone(IST).date().isoformat() != target):
        return {"status": "SAME_DAY_UNIVERSE_REQUIRED", "execution_enabled": False}
    from src.research_input_gate import prepare_research_inputs
    inputs = prepare_research_inputs(current["snapshot"], local, "RELIANCE", "2885")
    if inputs["status"] != "RESEARCH_INPUTS_READY":
        return inputs
    if inputs["reference_dates"] != expected_dates:
        return {"status": "CAPTURE_REFERENCE_DATES_MISMATCH", "execution_enabled": False}
    start = (local - timedelta(days=1)).strftime("%Y-%m-%d 09:15:00")
    end = (local + timedelta(days=1)).strftime("%Y-%m-%d 09:15:00")
    payload = fetch(token, "2885", 5, start, end)
    observed = clock()
    if observed.tzinfo is None or observed < now or observed.astimezone(IST).date() != local.date():
        raise ValueError("Capture clock moved backwards or crossed session")
    # First observation is after the broker response, never the pre-fetch clock.
    report = prepare_capture(payload, observed, current["revision"])
    return capture_store.save(report)


def main():
    if os.getenv("FORWARD_CAPTURE_ENABLED") != "true":
        print(json.dumps({"status": "FORWARD_CAPTURE_DISABLED", "execution_enabled": False}))
        return 0
    url = os.getenv("SCAN_DATABASE_URL", "")
    if not url.startswith(("postgresql://", "postgres://")):
        print(json.dumps({"status": "FORWARD_CAPTURE_STORE_REQUIRED", "execution_enabled": False}))
        return 1
    try:
        result = capture_once(datetime.now(IST), UniverseStore(url),
                              ForwardCaptureStore(url), os.getenv("DHAN_ACCESS_TOKEN"))
        report = result.get("report", {})
        print(json.dumps({"status": result["status"], "data_status": report.get("status"),
                          "new_candles": report.get("new_candles"),
                          "forward_paper_ready": False, "execution_enabled": False}))
        return 0
    except Exception as exc:
        # No credentials, URL, prices or broker exception messages in runtime logs.
        print(json.dumps({"status": "FORWARD_CAPTURE_FAILED", "error_type": type(exc).__name__,
                          "execution_enabled": False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

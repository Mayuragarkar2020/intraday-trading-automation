"""One existing cron: pre-market universe refresh, then RELIANCE research."""
from datetime import time
from zoneinfo import ZoneInfo
from src.market_schedule import research_window
from src.research_input_gate import prepare_research_inputs
from src.daily_universe_refresh import build_daily_universe
from src.dhan_scheduled_pipeline import process_once

IST = ZoneInfo("Asia/Kolkata")

def run_cycle(now, universe_store, scan_store, token, *, builder=build_daily_universe,
              scanner=process_once):
    active, reason = research_window(now, start=time(8,30), end=time(11,40))
    if not active:
        return {"status": reason, "execution_enabled": False}
    local = now.astimezone(IST)
    target = local.date().isoformat()
    universe_store.initialize()
    current = universe_store.latest(target)
    refreshed = False
    if current is None:
        if local.time() >= time(9,15):
            return {"status": "UNIVERSE_REFRESH_MISSING", "execution_enabled": False}
        report, evidence = builder(target)
        if report["target_date"] != target:
            raise ValueError("Refresh target mismatch")
        universe_store.publish(report, evidence)
        current = universe_store.latest(target)
        if current is None:
            raise ValueError("Refresh publication not readable")
        refreshed = True
    active, reason = research_window(now)
    if not active:
        return {"status": "UNIVERSE_REFRESHED" if refreshed else "UNIVERSE_READY",
                "revision": current["revision"], "execution_enabled": False}
    if not token:
        return {"status": "DHAN_TOKEN_NOT_CONFIGURED", "execution_enabled": False}
    inputs = prepare_research_inputs(current["snapshot"], now, "RELIANCE", "2885")
    if inputs["status"] != "RESEARCH_INPUTS_READY":
        return inputs
    result = scanner(token, "2885", "RELIANCE", now, scan_store,
                     reference_dates=inputs["reference_dates"])
    result["universe_revision"] = current["revision"]
    result["execution_enabled"] = False
    return result

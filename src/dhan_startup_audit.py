"""Safe one-shot Dhan data check during preview service startup.

Never logs tokens, full broker responses, prices or account identifiers.
Read-only historical candles, no order routes.
"""
import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from src.dhan_history_client import fetch_intraday
from src.dhan_candle_audit import audit_candles

LOG=logging.getLogger("dhan_validation")
IST=ZoneInfo("Asia/Kolkata")

def run_startup_audit():
    token=os.getenv("DHAN_ACCESS_TOKEN")
    if not token:
        LOG.warning("DHAN_AUDIT %s",json.dumps({"status":"TOKEN_NOT_CONFIGURED","orders_enabled":False}))
        return {"status":"TOKEN_NOT_CONFIGURED"}
    try:
        data=fetch_intraday(token,"2885",5,"2026-10-28 09:15:00","2026-10-30 15:30:00")
        n=len(data["timestamp"])
        if n==0:raise ValueError("Empty broker response")
        reports={}
        for assumption in (True,False):
            try:
                report=audit_candles(data,as_of=datetime.now(IST),
                                     timestamps_are_open=assumption,cas_eligible=None)
                reports["open" if assumption else "close"]={
                    "sessions":len(report["sessions"]),
                    "candle_count":report["candle_count"],
                    "missing_counts":[s["missing_count"] for s in report["sessions"]],
                    "missing_slots":[s["first_missing"] for s in report["sessions"]],
                    "dates":[s["date"] for s in report["sessions"]],
                    "first_close":[s["first_close"] for s in report["sessions"]],
                    "last_close":[s["last_close"] for s in report["sessions"]],
                }
            except (ValueError,OverflowError,TypeError) as exc:
                reports["open" if assumption else "close"]={"status":"INVALID","error_type":type(exc).__name__}
        # Compare the CAS 72-bar continuous-session reference separately.
        # This is a diagnostic hypothesis, NOT verified instrument eligibility.
        try:
            cas=audit_candles(data,as_of=datetime.now(IST),timestamps_are_open=True,cas_eligible=True)
            reports["cas_72_reference"]={"missing_slots":[s["first_missing"] for s in cas["sessions"]],
                "received":[s["received"] for s in cas["sessions"]],
                "session_complete":[s["session_complete"] for s in cas["sessions"]],
                "eligibility_verified":False,
                "safe_for_scanning":False,
                "reason":"CAS_ELIGIBILITY_AND_TIMESTAMP_NOT_VERIFIED"}
        except (ValueError,OverflowError,TypeError) as exc:
            reports["cas_72_reference"]={"status":"INVALID","error_type":type(exc).__name__}
        result={"status":"FETCHED_AUDITED","candidate_security_id":"2885",
                "timestamp_verified":False,"comparison":reports,"orders_enabled":False}
    except Exception as exc:
        result={"status":"FETCH_OR_AUDIT_FAILED","error_type":type(exc).__name__,
                "orders_enabled":False}
    LOG.warning("DHAN_AUDIT %s",json.dumps(result,separators=(",",":")))
    return result

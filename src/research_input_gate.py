"""Bind research scanning to the dated universe without granting trade eligibility."""
from datetime import datetime
import re
from zoneinfo import ZoneInfo
from src.universe_research import validate_dates

IST = ZoneInfo("Asia/Kolkata")

def prepare_research_inputs(report, now, symbol, security_id):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Timezone-aware clock required")
    def hold(status):
        return {"status": status, "execution_enabled": False}
    if (not isinstance(report, dict) or report.get("mode") != "LIQUIDITY_RESEARCH_ONLY"
            or report.get("execution_enabled") is not False or report.get("tradable_count") != 0):
        return hold("UNSAFE_UNIVERSE_SNAPSHOT")
    target = now.astimezone(IST).date().isoformat()
    if report.get("target_date") != target:
        return hold("UNIVERSE_SNAPSHOT_DATE_MISMATCH")
    try:
        sources = report["sources"]
        dates = [source["asof_date"] for source in sources]
        validate_dates(dates, target)
        if dates[-1] != report["asof_date"]:
            raise ValueError()
        if any(not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))
               or not isinstance(source.get("eq_rows"), int) or source["eq_rows"] <= 0
               for source in sources):
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        return hold("UNIVERSE_REFERENCE_DATES_INVALID")
    matches = [row for row in report.get("candidates", []) if row.get("symbol") == symbol]
    if len(matches) != 1:
        return hold("UNIVERSE_SYMBOL_NOT_UNIQUE")
    candidate = matches[0]
    if (candidate.get("reference_review_status") != "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"
            or candidate.get("liquidity_pass") is not True):
        return hold("UNIVERSE_SYMBOL_HELD_OR_EXCLUDED")
    if (candidate.get("mapping_status") != "UNIQUE"
            or candidate.get("dhan_security_id") != str(security_id)):
        return hold("UNIVERSE_DHAN_MAPPING_MISMATCH")
    return {"status": "RESEARCH_INPUTS_READY", "reference_dates": dates,
            "execution_enabled": False, "eligibility_verified": False}

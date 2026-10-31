"""Reproducible T-1 liquidity research. Never publishes trading eligibility."""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from src.ingestion import load_bhavcopy, DataQualityError
from src.screening import evaluate

def validate_dates(session_dates, target_date, required=20):
    if not isinstance(required, int) or isinstance(required, bool) or required != 20:
        raise DataQualityError("Research requires exactly 20 sessions")
    try:
        parsed = [date.fromisoformat(d) for d in session_dates]
        target = date.fromisoformat(target_date)
    except (TypeError, ValueError):
        raise DataQualityError("ISO session and target dates required") from None
    if any(d.isoformat() != s for d, s in zip(parsed, session_dates)) or target.isoformat() != target_date:
        raise DataQualityError("Canonical ISO dates required")
    if len(parsed) != required or parsed != sorted(set(parsed)):
        raise DataQualityError("Exactly 20 distinct ascending sessions required")
    if parsed[-1] >= target:
        raise DataQualityError("T-1 history must precede target date")
    return parsed

def build_research(session_paths, target_date, cfg, mapping=None):
    """session_paths is an ordered list of (ISO date, official CSV/ZIP path).

    Dates are explicitly supplied, not inferred by subtracting weekdays.
    Completeness of the exchange calendar and restrictions are separate gates.
    """
    dates = [d for d, _ in session_paths]
    validate_dates(dates, target_date, cfg["universe"]["required_history_sessions"])
    histories = defaultdict(list)
    manifests = []
    latest = set()
    for day, path in session_paths:
        rows, manifest = load_bhavcopy(Path(path), day)
        manifests.append(manifest)
        for row in rows:
            histories[row["isin"]].append(row)
        latest = {row["isin"] for row in rows}
    candidates, incomplete = [], []
    failed_rules = Counter()
    excluded = 0
    for isin in sorted(latest):
        rows = histories[isin]
        if [r["date"] for r in rows] != dates:
            incomplete.append({"isin": isin, "symbol": rows[-1]["symbol"],
                               "missing_dates": sorted(set(dates)-{r["date"] for r in rows})})
            continue
        decision = evaluate(rows, cfg)
        if not decision["liquidity_pass"]:
            excluded += 1
            failed_rules.update(decision["failed_rules"])
            continue
        ids = (mapping or {}).get(isin, [])
        decision["status"] = "HOLD_RESTRICTIONS_AND_CALENDAR"
        decision["mapping_status"] = "UNIQUE" if len(ids) == 1 else ("MISSING" if not ids else "AMBIGUOUS")
        if len(ids) == 1:
            decision["dhan_security_id"] = ids[0]
        candidates.append(decision)
    candidates.sort(key=lambda row: (-float(row["metrics"]["avg_turnover_20d_cr"]), row["isin"]))
    return {
        "mode": "LIQUIDITY_RESEARCH_ONLY", "execution_enabled": False,
        "target_date": target_date, "asof_date": dates[-1],
        "calendar_completeness_verified": False, "restrictions_verified": False,
        "tradable_count": 0, "config": cfg, "sources": manifests,
        "summary": {"latest_eq_count": len(latest), "complete_history_count": len(latest)-len(incomplete),
                    "incomplete_history_count": len(incomplete), "excluded_liquidity_count": excluded,
                    "liquidity_candidate_count": len(candidates),
                    "unique_dhan_mapping_count": sum(r["mapping_status"] == "UNIQUE" for r in candidates),
                    "failed_rule_counts": dict(sorted(failed_rules.items()))},
        "candidates": candidates, "incomplete_histories": incomplete,
        "remaining_gates": ["Verify effective-dated security eligibility, fixed bands and surveillance",
                            "Verify full exchange session calendar and latest completed session",
                            "Validate corporate actions and Dhan candle/chart reconciliation"]
    }

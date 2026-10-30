"""Pure T-1 liquidity calculations. Never uses subsequent session data."""
from __future__ import annotations
from decimal import Decimal
from statistics import median

CR = Decimal("10000000")

class ScreeningError(ValueError):
    pass

def evaluate(rows: list[dict], cfg: dict) -> dict:
    """Evaluate one ISIN, with rows ordered by date ascending, 20 sessions exactly."""
    universe = cfg["universe"]
    limits = cfg["liquidity"]
    required = int(universe["required_history_sessions"])
    if len(rows) != required or len({r["date"] for r in rows}) != required:
        raise ScreeningError("Incomplete or duplicated session history")
    if rows != sorted(rows, key=lambda r: r["date"]):
        raise ScreeningError("Sessions out of order")
    if len({r["isin"] for r in rows}) != 1:
        raise ScreeningError("Multiple ISINs in history")
    turns = [r["turnover_inr"] / CR for r in rows]
    avg = sum(turns) / Decimal(len(turns))
    med = Decimal(str(median(turns)))
    latest = turns[-1]
    min5 = min(turns[-5:])
    ratio = latest / avg if avg > 0 else Decimal("0")
    close = rows[-1]["close"]
    checks = {
        "E04_PRICE": Decimal(str(universe["price_min"])) <= close <= Decimal(str(universe["price_max"])),
        "L01_AVG20": avg >= Decimal(str(limits["avg_turnover_20d_min_cr"])),
        "L02_MED20": med >= Decimal(str(limits["median_turnover_20d_min_cr"])),
        "L03_LAST": latest >= Decimal(str(limits["last_turnover_min_cr"])),
        "L04_RATIO": ratio >= Decimal(str(limits["last_to_avg_ratio_min"])),
        "L05_MIN5": min5 >= Decimal(str(limits["min_turnover_5d_cr"])),
        "L06_VOLUME": all(r["volume"] > 0 for r in rows),
    }
    metrics = {"close": str(close), "avg_turnover_20d_cr": str(avg),
               "median_turnover_20d_cr": str(med), "last_turnover_cr": str(latest),
               "min_turnover_5d_cr": str(min5), "activity_ratio": str(ratio),
               "avg_volume_20d": str(Decimal(sum(r["volume"] for r in rows)) / Decimal(required))}
    return {"isin": rows[-1]["isin"], "symbol": rows[-1]["symbol"],
            "asof_date": rows[-1]["date"], "metrics": metrics,
            "liquidity_pass": all(checks.values()),
            "failed_rules": [code for code, ok in checks.items() if not ok]}

def provisional_status(decision: dict) -> str:
    """An absent restriction/security/broker validation must never approve a security."""
    return "HOLD_RESTRICTIONS_AND_MAPPING" if decision["liquidity_pass"] else "EXCLUDED_LIQUIDITY"

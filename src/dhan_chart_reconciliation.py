"""Compare a fixed user-supplied chart observation with read-only Dhan data.

A single matching candle is scoped evidence, never permission to trade or a
verification of every session/instrument. No credentials or broker calls here.
"""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
CHART_OPEN = datetime(2026, 10, 30, 9, 15, tzinfo=IST)
CHART_OHLC = dict(zip(("open", "high", "low", "close"),
                      map(Decimal, ("1170.40", "1174.60", "1162.70", "1164.30"))))
FIELDS = ("timestamp", "open", "high", "low", "close", "volume")


def reconcile_reliance_chart(payload):
    """Require exact prices; compare both start- and end-labelled hypotheses."""
    if not isinstance(payload, dict) or any(not isinstance(payload.get(k), list) for k in FIELDS):
        raise ValueError("Invalid candle arrays")
    count = len(payload["timestamp"])
    if not 1 <= count <= 1000 or any(len(payload[k]) != count for k in FIELDS):
        raise ValueError("Invalid candle array lengths")
    rows = {}
    previous = None
    for i in range(count):
        try:
            if any(isinstance(payload[k][i], bool) for k in FIELDS):
                raise ValueError("Boolean candle value")
            values = {k: Decimal(str(payload[k][i])) for k in FIELDS}
            if any(not v.is_finite() for v in values.values()):
                raise ValueError("Nonfinite candle value")
            epoch = values["timestamp"]
            volume = values["volume"]
            if epoch != epoch.to_integral_value() or not 946684800 <= epoch <= 4102444800:
                raise ValueError("Invalid epoch")
            if volume < 0 or volume != volume.to_integral_value():
                raise ValueError("Invalid volume")
            if not (0 < values["low"] <= values["open"] <= values["high"]
                    and values["low"] <= values["close"] <= values["high"]):
                raise ValueError("Invalid OHLC")
            stamp = datetime.fromtimestamp(int(epoch), IST)
            if stamp.second or stamp.microsecond or stamp.minute % 5:
                raise ValueError("Unaligned timestamp")
            if previous is not None and stamp <= previous:
                raise ValueError("Duplicate or unordered timestamps")
            previous = stamp
            rows[stamp] = {k: values[k] for k in CHART_OHLC}
        except (InvalidOperation, TypeError, OverflowError, OSError) as exc:
            raise ValueError("Invalid candle value") from exc
    candidates = {}
    matches = []
    for convention, stamp in (("OPEN", CHART_OPEN), ("CLOSE", CHART_OPEN + timedelta(minutes=5))):
        actual = rows.get(stamp)
        matched = actual == CHART_OHLC
        if matched:
            matches.append(convention)
        candidates[convention] = {
            "raw_timestamp_ist": stamp.isoformat(), "present": actual is not None,
            "ohlc": {k: str(v) for k, v in actual.items()} if actual else None,
            "exact_match": matched,
        }
    status = "SAMPLE_MATCHED" if len(matches) == 1 else "AMBIGUOUS" if matches else "NO_MATCH"
    return {
        "status": status, "symbol": "RELIANCE", "security_id": "2885",
        "exchange": "NSE_EQ", "interval_minutes": 5,
        "chart_open_ist": CHART_OPEN.isoformat(),
        "chart_ohlc": {k: str(v) for k, v in CHART_OHLC.items()},
        "observation_source": "USER_DHAN_CHART_SCREENSHOT_2026_10_31",
        "matching_convention": matches[0] if len(matches) == 1 else None,
        "candidates": candidates,
        "scope": "ONE_HISTORICAL_CANDLE_ONLY",
        "timestamp_convention_verified": False,
        "cas_eligibility_verified": False,
        "forward_paper_ready": False, "execution_enabled": False,
    }

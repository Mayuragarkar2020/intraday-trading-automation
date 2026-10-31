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


def _reconcile_chart(payload, chart_open, chart_ohlc):
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
            rows[stamp] = {k: values[k] for k in chart_ohlc}
        except (InvalidOperation, TypeError, OverflowError, OSError) as exc:
            raise ValueError("Invalid candle value") from exc
    candidates = {}
    matches = []
    for convention, stamp in (("OPEN", chart_open), ("CLOSE", chart_open + timedelta(minutes=5))):
        actual = rows.get(stamp)
        matched = actual == chart_ohlc
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
        "chart_open_ist": chart_open.isoformat(),
        "chart_ohlc": {k: str(v) for k, v in chart_ohlc.items()},
        "observation_source": "USER_DHAN_CHART_SCREENSHOT_2026_10_31",
        "matching_convention": matches[0] if len(matches) == 1 else None,
        "candidates": candidates,
        "scope": "ONE_HISTORICAL_CANDLE_ONLY",
        "timestamp_convention_verified": False,
        "cas_eligibility_verified": False,
        "forward_paper_ready": False, "execution_enabled": False,
    }


def reconcile_reliance_chart(payload):
    """Preserve the original fixed 09:15 comparison and its response contract."""
    return _reconcile_chart(payload, CHART_OPEN, CHART_OHLC)


CLOSING_CHART_SAMPLES = tuple(
    (datetime(2026,10,30,15,minute,tzinfo=IST),
     dict(zip(("open","high","low","close"),map(Decimal,prices))))
    for minute,prices in (
        (5,("1161.30","1163.50","1160.50","1163.30")),
        (10,("1163.30","1163.90","1158.40","1159.00")),
    )
)


def reconcile_reliance_closing_chart(payload):
    """Two user screenshots; no assertion that an absent candle proves closure."""
    import hashlib
    import json
    samples = [_reconcile_chart(payload,stamp,prices) for stamp,prices in CLOSING_CHART_SAMPLES]
    conventions = [s["matching_convention"] for s in samples]
    matched = [c for c in conventions if c is not None]
    if any(s["status"] == "AMBIGUOUS" for s in samples):
        status = "AMBIGUOUS"
    elif len(matched) == 2:
        status = "ALL_SAMPLES_MATCHED" if len(set(matched)) == 1 else "INCONSISTENT_CONVENTIONS"
    else:
        status = "PARTIAL_MATCH" if matched else "NO_MATCH"
    # _reconcile_chart validated all arrays, epochs and ordering before this metadata.
    stamps = [datetime.fromtimestamp(int(Decimal(str(v))),IST) for v in payload["timestamp"]]
    target = [s for s in stamps if s.date() == CLOSING_CHART_SAMPLES[0][0].date()]
    boundary = datetime(2026,10,30,15,15,tzinfo=IST)
    canonical = json.dumps({k:payload[k] for k in FIELDS},sort_keys=True,separators=(",",":"),default=str)
    return {"status":status, "symbol":"RELIANCE", "security_id":"2885",
        "exchange":"NSE_EQ", "interval_minutes":5, "samples":samples,
        "matching_convention":matched[0] if status == "ALL_SAMPLES_MATCHED" else None,
        "observation_source":"TWO_USER_DHAN_CHART_SCREENSHOTS_2026_10_31",
        "decoded_payload_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
        "raw_target_session_count":len(target),
        "first_raw_timestamp_ist":target[0].isoformat() if target else None,
        "last_raw_timestamp_ist":target[-1].isoformat() if target else None,
        "raw_timestamps_at_or_after_15_15":[s.isoformat() for s in target if s >= boundary],
        "scope":"TWO_HISTORICAL_CLOSING_CANDLES_ONLY",
        "chart_last_visible_label_ist":CLOSING_CHART_SAMPLES[-1][0].isoformat(),
        "boundary_interpretation":"UNVERIFIED_NO_AUCTION_FILL_INFERENCE",
        "timestamp_convention_verified":False, "cas_eligibility_verified":False,
        "forward_paper_ready":False, "execution_enabled":False}


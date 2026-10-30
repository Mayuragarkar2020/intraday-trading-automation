"""Read-only historical candle diagnostics from Dhan responses.

Timestamp convention is explicitly a research assumption until reconciled
against a known Dhan chart. Never creates actionable signals.
"""
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.candle_pipeline import ema
from src.session_vwap import session_vwap
from src.candle_session import ensure_ordered_session

IST=ZoneInfo("Asia/Kolkata")

def historical_diagnostics(payload,*,timestamps_are_open,as_of):
    records=normalize_dhan_intraday(payload,as_of=as_of,
                 timestamps_are_open=timestamps_are_open)
    if not records:
        return {"status":"NO_COMPLETE_CANDLES","candle_count":0,"execution_enabled":False}
    sessions=defaultdict(list)
    for c in records:
        sessions[c.time[:10]].append(c.as_candle())
    valid=[]
    for day,items in sorted(sessions.items()):
        # Do not silently compute session VWAP with missing opening bars.
        if items[0].time[11:16]!="09:20":
            continue
        try:ensure_ordered_session([c.time for c in items])
        except ValueError:continue
        valid.extend(items)
    if len(valid)<20:
        return {"status":"INSUFFICIENT_VALID_HISTORY","candle_count":len(records),
                "valid_candles":len(valid),"execution_enabled":False}
    closes=[c.close for c in valid]
    last=valid[-1]
    current_session=[c for c in valid if c.time[:10]==last.time[:10]]
    result={"status":"HISTORICAL_INDICATORS_ONLY",
            "candle_count":len(records),"valid_candles":len(valid),
            "last_completed_close":last.time,"last_close":str(last.close),
            "ema10":str(ema(closes,10)),"ema20":str(ema(closes,20)),
            "session_vwap":str(session_vwap(current_session)),
            "timestamp_assumption":"OPEN" if timestamps_are_open else "CLOSE",
            "timestamp_convention_verified":False,"setup_qualified":False,
            "reason":"Requires 20-session time-slot volume and completed 15m trend checks",
            "execution_enabled":False}
    return result

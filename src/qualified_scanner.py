"""Strict, fail-closed indicator preparation from completed five-minute candles.

Uses historical closes for EMA warm-up, current-session OHLCV for VWAP,
20 matching historical time slots for relative volume, and *completed*
15-minute candles for higher-timeframe trend.
"""
from datetime import timedelta
from decimal import Decimal
from src.candle_pipeline import ema
from src.candle_session import ensure_ordered_session,parse_close
from src.session_vwap import session_vwap
from src.setup_detector import Bar,detect_setup

D=lambda x:Decimal(str(x))

def baseline_for_slot(previous_sessions,slot,days=20):
    if len(previous_sessions)<days:raise ValueError("Insufficient historical sessions")
    volumes=[]
    unique=set()
    for session in previous_sessions[-days:]:
        if not session:raise ValueError("Empty historical session")
        day=ensure_ordered_session([c.time for c in session])
        if day in unique:raise ValueError("Duplicate historical session")
        unique.add(day)
        matches=[c for c in session if parse_close(c.time).strftime("%H:%M")==slot]
        if len(matches)!=1 or matches[0].volume<=0:
            raise ValueError("Missing or invalid historical time slot")
        volumes.append(matches[0].volume)
    return D(sum(volumes))/D(days)

def higher_tf_confirmed(candles_15m):
    """Requires pre-aggregated, chronologically ordered completed 15m bars."""
    if len(candles_15m)<21:raise ValueError("Insufficient 15m warm-up")
    times=[parse_close(c.time) for c in candles_15m]
    if any(t.minute%15!=0 or t.second for t in times):
        raise ValueError("15m candles must end at :00, :15, :30 or :45")
    if any(b<=a for a,b in zip(times,times[1:])):raise ValueError("Non-increasing 15m candles")
    closes=[c.close for c in candles_15m]
    current10=ema(closes,10);current20=ema(closes,20)
    previous10=ema(closes[:-1],10);previous20=ema(closes[:-1],20)
    return bool(current10>current20 and current10>previous10 and current20>previous20)

def qualify(completed_5m,previous_sessions,completed_15m,ema_warmup_closes):
    """Never returns ARMED when required source history is unavailable."""
    try:
        current_day=ensure_ordered_session([c.time for c in completed_5m])
        if parse_close(completed_5m[0].time).strftime("%H:%M")!="09:20":
            raise ValueError("VWAP needs complete candles from session open")
        latest_5m=parse_close(completed_5m[-1].time)
        if not completed_15m:raise ValueError("Missing higher timeframe")
        latest_15m=parse_close(completed_15m[-1].time)
        if latest_15m>latest_5m or latest_5m-latest_15m>timedelta(minutes=15):
            raise ValueError("Stale or future higher timeframe confirmation")
        if any(ensure_ordered_session([c.time for c in session])>=current_day for session in previous_sessions):
            raise ValueError("Prior session history must precede current session")
        if len(completed_5m)<3 or len(ema_warmup_closes)<20:
            raise ValueError("Insufficient candles")
        higher=higher_tf_confirmed(completed_15m)
        bars=[]
        for n in range(len(completed_5m)-2,len(completed_5m)+1):
            sub=completed_5m[:n]
            slot=parse_close(sub[-1].time).strftime("%H:%M")
            baseline=baseline_for_slot(previous_sessions,slot)
            closes=[*ema_warmup_closes,*[c.close for c in sub]]
            c=sub[-1]
            bars.append(Bar(c.time,c.open,c.high,c.low,c.close,c.volume,
                  ema(closes,10),ema(closes,20),session_vwap(sub),
                  D(c.volume)/baseline,higher))
        return detect_setup(bars)
    except (ValueError,TypeError,ArithmeticError,IndexError) as exc:
        from src.setup_detector import Signal
        return Signal("BLOCK","INCOMPLETE_OR_INVALID_INDICATOR_DATA")

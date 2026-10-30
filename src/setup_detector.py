"""Offline, long-only 5-minute range-breakout signal detector.

All indicators must be supplied from completed candles; no live order placement.
A breakout is actionable only if its trigger is crossed by a later candle.
"""
from dataclasses import dataclass
from decimal import Decimal
from src.candle_session import ensure_ordered_session

def D(x):return Decimal(str(x))

@dataclass(frozen=True)
class Bar:
    time:str
    open:Decimal
    high:Decimal
    low:Decimal
    close:Decimal
    volume:int
    ema10:Decimal
    ema20:Decimal
    vwap:Decimal
    rel_volume:Decimal
    higher_tf_bullish:bool

@dataclass(frozen=True)
class Signal:
    status:str
    reason:str
    range_high:Decimal|None=None
    range_low:Decimal|None=None
    trigger:Decimal|None=None
    initial_stop:Decimal|None=None

def detect_setup(bars,minimum_range_candles=3,buffer=Decimal("0.05"),
                 min_relative_volume=Decimal("1.2"), max_range_pct=Decimal("0.025")):
    if len(bars)<minimum_range_candles:
        return Signal("WAIT","NEED_COMPLETED_RANGE_CANDLES")
    if minimum_range_candles<3:raise ValueError("Minimum range cannot be below three candles")
    buffer=D(buffer);min_relative_volume=D(min_relative_volume)
    if buffer<=0 or min_relative_volume<=0:raise ValueError("Invalid configuration")
    window=bars[-minimum_range_candles:]
    if any(x.high<x.low or x.low<=0 or x.close<=0 or x.volume<0 for x in window):
        return Signal("BLOCK","INVALID_OHLCV")
    if all("T" in x.time for x in window):
        try:ensure_ordered_session([x.time for x in window])
        except ValueError:return Signal("BLOCK","INVALID_CANDLE_SESSION_OR_GAPS")
    latest=window[-1]
    if not all(x.ema10>x.ema20 for x in window):
        return Signal("WAIT","EMA_ALIGNMENT_MISSING")
    if not all(x.close>x.ema10 and x.close>x.ema20 and x.close>x.vwap for x in window):
        return Signal("WAIT","PRICE_NOT_ABOVE_TRENDS")
    if not latest.higher_tf_bullish:
        return Signal("WAIT","HIGHER_TIMEFRAME_NOT_BULLISH")
    if latest.rel_volume<min_relative_volume:
        return Signal("WAIT","RELATIVE_VOLUME_INSUFFICIENT")
    top=max(x.high for x in window);bottom=min(x.low for x in window)
    if (top-bottom)/latest.close>D(max_range_pct):
        return Signal("WAIT","CONSOLIDATION_RANGE_TOO_WIDE")
    stop=bottom-buffer
    if stop<=0:return Signal("BLOCK","INVALID_STOP")
    return Signal("ARMED","WAIT_FOR_NEXT_CANDLE_BREAKOUT",top,bottom,top+buffer,stop)

def confirm_breakout(signal,next_bar):
    if signal.status!="ARMED":return "BLOCK_NOT_ARMED"
    if next_bar.low<=signal.initial_stop:return "INVALIDATED_STOP_TOUCHED"
    if next_bar.high>=signal.trigger:return "BREAKOUT_TRIGGERED"
    return "WAITING_FOR_BREAKOUT"

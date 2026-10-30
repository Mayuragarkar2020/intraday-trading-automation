"""Pure trade-management decisions for an already-filled long trade.

Signals are *instructions*, not broker fills or confirmation of stop modifications.
"""
from dataclasses import dataclass,replace
from decimal import Decimal

@dataclass(frozen=True)
class ManagedLong:
    entry:Decimal
    initial_stop:Decimal
    quantity:int
    estimated_roundtrip_cost_per_share:Decimal
    high_since_fill:Decimal
    low_since_fill:Decimal
    break_even_requested:bool=False
    closed:bool=False

def open_long(entry,stop,quantity,estimated_roundtrip_cost_per_share):
    entry,stop,cost=map(Decimal,map(str,(entry,stop,estimated_roundtrip_cost_per_share)))
    if not (entry>stop>0) or quantity<=0 or cost<0:
        raise ValueError("Invalid filled trade")
    return ManagedLong(entry,stop,quantity,cost,entry,entry)

def on_completed_candle(trade,high,low,close,ema10):
    if trade.closed:return trade,"ALREADY_CLOSED"
    high,low,close,ema10=map(Decimal,map(str,(high,low,close,ema10)))
    if not (high>=max(close,low) and low>0 and ema10>0):
        raise ValueError("Invalid candle values")
    t=replace(trade,high_since_fill=max(trade.high_since_fill,high),
              low_since_fill=min(trade.low_since_fill,low))
    # An already-hit protective stop must not be treated as an assured fill.
    if low<=trade.initial_stop and not trade.break_even_requested:
        return t,"RECONCILE_STOP_EXECUTION"
    if close<ema10:
        return t,"REQUEST_EXIT_EMA10_CLOSE"
    initial_r=trade.entry-trade.initial_stop
    if not t.break_even_requested and high>=trade.entry+Decimal("1.5")*initial_r:
        return replace(t,break_even_requested=True),"REQUEST_STOP_TO_COST_BREAKEVEN"
    return t,"HOLD"

def excursion(trade):
    price_risk=trade.entry-trade.initial_stop
    return {"mfe_per_share":trade.high_since_fill-trade.entry,
            "mae_per_share":trade.entry-trade.low_since_fill,
            "mfe_r":(trade.high_since_fill-trade.entry)/price_risk,
            "mae_r":(trade.entry-trade.low_since_fill)/price_risk,
            "breakeven_stop_requested":trade.entry+trade.estimated_roundtrip_cost_per_share}

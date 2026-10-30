"""Candle-close indicator pipeline and deterministic DEMO shortlist; never live data."""
from dataclasses import dataclass
from decimal import Decimal
from src.setup_detector import Bar,detect_setup

D=lambda x:Decimal(str(x))

@dataclass(frozen=True)
class Candle:
    time:str
    open:Decimal
    high:Decimal
    low:Decimal
    close:Decimal
    volume:int

def ema(values,period):
    if len(values)<period:return None
    k=D(2)/D(period+1)
    out=sum(values[:period])/D(period)
    for value in values[period:]:out=(value-out)*k+out
    return out

def indicators(candles,prior_slot_volume,htf_bullish=True):
    """Use completed *same-session* candles for VWAP and completed history for EMAs."""
    if not candles or prior_slot_volume<=0:raise ValueError("Missing candles or relative-volume baseline")
    if any(c.high<c.low or c.low<=0 or c.volume<0 or not(c.low<=c.close<=c.high) for c in candles):
        raise ValueError("Invalid OHLCV")
    closes=[c.close for c in candles]
    if len(closes)<20:return None
    weighted=sum(((c.high+c.low+c.close)/D(3))*c.volume for c in candles)
    volume=sum(c.volume for c in candles)
    if volume<=0:raise ValueError("Zero session volume")
    c=candles[-1]
    return Bar(c.time,c.open,c.high,c.low,c.close,c.volume,
               ema(closes,10),ema(closes,20),weighted/D(volume),
               D(c.volume)/D(prior_slot_volume),htf_bullish)

def scan_demo():
    """Synthetic, non-actionable samples demonstrating calculated indicators and setup decisions."""
    output=[]
    scenarios=[("RELIANCE","ARMED"),("ICICIBANK","FORMING"),("INFY","WEAK_VOLUME")]
    for symbol,kind in scenarios:
        candles=[]
        for i in range(40):
            close=D(950)+D(i)*D(1.3)
            if i>=37:close=D("1002")
            candles.append(Candle(str(i),close-D("0.5"),close+D("1"),close-D("1"),close,1000))
        bars=[]
        for end in (38,39,40):
            current=indicators(candles[:end],2000 if kind=="WEAK_VOLUME" else 500)
            bars.append(current)
        if kind=="FORMING":
            signal=detect_setup(bars[-2:])
        else:signal=detect_setup(bars)
        output.append({"symbol":symbol,"mode":"SYNTHETIC_DEMO","status":signal.status,
          "reason":signal.reason,"entry":str(signal.trigger) if signal.trigger is not None else None,
          "stop":str(signal.initial_stop) if signal.initial_stop is not None else None,
          "ema10":str(bars[-1].ema10),"ema20":str(bars[-1].ema20),
          "vwap":str(bars[-1].vwap),"relative_volume":str(bars[-1].rel_volume)})
    return output

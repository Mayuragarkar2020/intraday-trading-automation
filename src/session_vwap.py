"""Session-aware VWAP computed only from completed NSE 5-minute candles."""
from decimal import Decimal
from src.candle_session import ensure_ordered_session

def session_vwap(candles):
    """Candles must be consecutive, timezone-aware, same-session 5m closes."""
    ensure_ordered_session([x.time for x in candles])
    if any(x.volume<0 or x.low<=0 or x.high<x.low or not x.low<=x.close<=x.high for x in candles):
        raise ValueError("Invalid OHLCV")
    volume=sum(x.volume for x in candles)
    if volume<=0:raise ValueError("Zero volume")
    return sum(((x.high+x.low+x.close)/Decimal(3))*x.volume for x in candles)/Decimal(volume)

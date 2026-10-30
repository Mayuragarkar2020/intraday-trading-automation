"""DhanHQ v2 5m OHLCV response adapter, no network access or order APIs.

Dhan exposes parallel arrays and Unix epoch timestamps. Timestamp semantics
(start versus close of candle) must be confirmed against live broker charts.
"""
from datetime import datetime,timedelta
from decimal import Decimal,InvalidOperation
from zoneinfo import ZoneInfo
from src.candle_input import CandleInput
from src.candle_session import parse_close

IST=ZoneInfo("Asia/Kolkata")
FIELDS=("timestamp","open","high","low","close","volume")

def normalize_dhan_intraday(payload,*,as_of,interval=5,timestamps_are_open=None):
    if timestamps_are_open is not True and timestamps_are_open is not False:
        raise ValueError("Dhan candle timestamp convention unverified")
    if interval!=5:raise ValueError("Expected five-minute Dhan candles")
    if as_of.tzinfo is None:raise ValueError("Timezone-aware as_of required")
    if not isinstance(payload,dict) or any(not isinstance(payload.get(k),list) for k in FIELDS):
        raise ValueError("Missing Dhan parallel OHLCV arrays")
    n=len(payload["timestamp"])
    if n==0 or any(len(payload[k])!=n for k in FIELDS):
        raise ValueError("Empty or mismatched OHLCV arrays")
    out=[]
    for i in range(n):
        ts=payload["timestamp"][i]
        if isinstance(ts,bool) or not isinstance(ts,(int,float,str,Decimal)):
            raise ValueError("Invalid epoch")
        try:
            numeric=Decimal(str(ts))
            if not numeric.is_finite() or numeric!=numeric.to_integral_value():
                raise ValueError("Invalid epoch")
            # Dhan returns Unix seconds; do not silently interpret milliseconds.
            seconds=int(numeric)
            if not 946684800<=seconds<=4102444800:
                raise ValueError("Invalid epoch")
            dt=datetime.fromtimestamp(seconds,IST)
        except (InvalidOperation,OverflowError,OSError,TypeError) as exc:
            raise ValueError("Invalid epoch") from exc
        if timestamps_are_open:dt+=timedelta(minutes=5)
        # Do not accept a candle that is not demonstrably complete.
        if dt>as_of.astimezone(IST):continue
        try:
            o,h,l,c=[Decimal(str(payload[k][i])) for k in ("open","high","low","close")]
            v=payload["volume"][i]
            if any(not x.is_finite() for x in (o,h,l,c)) or not (l<=o<=h and l<=c<=h and l>0):
                raise ValueError("Invalid OHLC")
            if isinstance(v,bool) or not isinstance(v,int) or v<0:raise ValueError("Invalid volume")
            parse_close(dt.isoformat())
            out.append(CandleInput(time=dt.isoformat(),open=o,high=h,low=l,close=c,volume=v))
        except (InvalidOperation,ValueError,TypeError) as exc:
            raise ValueError("Invalid Dhan candle values or session timestamp") from exc
    times=[x.time for x in out]
    if len(set(times))!=len(times) or times!=sorted(times):
        raise ValueError("Dhan timestamps duplicate or out of order")
    return out

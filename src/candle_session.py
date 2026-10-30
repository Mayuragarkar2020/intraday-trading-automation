"""Strict NSE five-minute session handling; no cross-session range formation."""
from datetime import datetime,time,timedelta
from zoneinfo import ZoneInfo

IST=ZoneInfo("Asia/Kolkata")
OPEN=time(9,15)
CLOSE=time(15,30)

def parse_close(timestamp):
    """Accept ISO timestamps with offsets; require explicit timezone and 5m close alignment."""
    value=datetime.fromisoformat(timestamp)
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Candle timestamps must include UTC offset")
    local=value.astimezone(IST)
    if local.weekday()>=5 or not OPEN<local.time()<=CLOSE:
        raise ValueError("Candle outside normal weekday NSE session")
    minutes=local.hour*60+local.minute-(9*60+15)
    if minutes%5 or local.second or local.microsecond:
        raise ValueError("Unaligned 5m closing timestamp")
    return local

def session_key(timestamp):
    return parse_close(timestamp).date().isoformat()

def ensure_ordered_session(closes):
    if not closes:raise ValueError("No candle closes")
    parsed=[parse_close(x) for x in closes]
    if any(b-a!=timedelta(minutes=5) for a,b in zip(parsed,parsed[1:])):
        raise ValueError("Missing, duplicate or cross-session 5m candles")
    return parsed[-1].date().isoformat()

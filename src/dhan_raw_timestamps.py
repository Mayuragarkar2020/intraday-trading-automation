"""Raw Dhan timestamp coverage diagnostics without OHLCV normalization."""
from collections import defaultdict
from datetime import datetime,timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

IST=ZoneInfo("Asia/Kolkata")
def raw_timestamp_report(payload):
    timestamps=payload.get("timestamp")
    if not isinstance(timestamps,list) or not timestamps:raise ValueError("Missing timestamps")
    sessions=defaultdict(list)
    for value in timestamps:
        if isinstance(value,bool):raise ValueError("Invalid epoch")
        number=Decimal(str(value))
        if not number.is_finite() or number!=number.to_integral_value():
            raise ValueError("Invalid epoch")
        seconds=int(number)
        if not 946684800<=seconds<=4102444800:raise ValueError("Invalid epoch")
        t=datetime.fromtimestamp(seconds,IST)
        sessions[t.date().isoformat()].append(t)
    out=[]
    for day,items in sorted(sessions.items()):
        times=sorted(items)
        hhmm=[x.strftime("%H:%M") for x in times]
        out.append({"date":day,"count":len(items),
                    "first_raw_ist":hhmm[:5],"last_raw_ist":hhmm[-5:],
                    "first_epoch":int(times[0].timestamp()),"last_epoch":int(times[-1].timestamp()),
                    "duplicate_count":len(items)-len(set(items))})
    return {"status":"RAW_TIMESTAMP_REPORT","timestamp_convention_verified":False,
            "sessions":out,"execution_enabled":False}

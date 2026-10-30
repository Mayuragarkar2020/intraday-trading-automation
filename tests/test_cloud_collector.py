from datetime import datetime
from zoneinfo import ZoneInfo
from src.cloud_collector import CheckpointCollector,eligible_close
from src.candle_input import BatchInput

IST=ZoneInfo("Asia/Kolkata")
def clock(h,m,s=15):
    return datetime(2026,11,2,h,m,s,tzinfo=IST)

def batch():
    stamp=lambda h,m:f"2026-11-02T{h:02d}:{m:02d}:00+05:30"
    bar=lambda t:{"time":t,"open":"100","high":"101","low":"99","close":"100","volume":1000}
    current=[bar(stamp(9,m)) for m in [20,25,30]]
    prior=[]
    from datetime import date,timedelta
    d=date(2026,10,30)
    while len(prior)<20:
        if d.weekday()<5:prior.append([bar(f"{d.isoformat()}T09:20:00+05:30"),bar(f"{d.isoformat()}T09:25:00+05:30"),bar(f"{d.isoformat()}T09:30:00+05:30")])
        d-=timedelta(days=1)
    # The 15-minute source is deliberately short: fail-closed signal, successful checkpoint
    htf=[bar(f"2026-10-30T09:{(30+i*15)%60:02d}:00+05:30") for i in range(21)]
    return BatchInput.model_validate({"candidates":[{"symbol":"RELIANCE","completed_5m":current,
        "previous_sessions":prior,"completed_15m":htf,
        "ema_warmup_closes":["99"]*20}]})

def test_exact_five_minute_close_with_settlement():
    assert eligible_close(clock(9,30,15)).strftime("%H:%M")=="09:30"
    assert eligible_close(clock(9,30,5)).strftime("%H:%M")=="09:25"
    assert eligible_close(clock(9,16)) is None
    assert eligible_close(clock(16,0)) is None

def test_checkpoint_does_not_repeat(tmp_path):
    collector=CheckpointCollector(tmp_path/"checkpoint.db")
    first=collector.scan(clock(9,30),batch())
    assert first["status"]=="SCANNED"
    assert first["setups"][0]["status"]=="BLOCK"
    second=collector.scan(clock(9,30),batch())
    assert second["status"]=="ALREADY_SCANNED"
    again=CheckpointCollector(tmp_path/"checkpoint.db")
    assert again.scan(clock(9,30),batch())["status"]=="ALREADY_SCANNED"

def test_missing_latest_bar_is_not_checkpointed(tmp_path):
    collector=CheckpointCollector(tmp_path/"checkpoint.db")
    assert collector.scan(clock(9,35),batch())["status"]=="WAIT_FOR_COMPLETE_CANDLES"
    assert collector.scan(clock(9,30),batch())["status"]=="SCANNED"

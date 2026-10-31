"""One-shot read-only Dhan -> scanner -> Postgres research snapshot.

No orders, no account endpoints. Resume is idempotent by candle-close primary key.
A missing candle, insufficient history or stale feed prevents persistence.
"""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_history_client import fetch_intraday
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.dhan_rvol_research import validated_session_groups
from src.dhan_research_scanner import aggregate_15m
from src.candle_input import BatchInput,CandidateInput,scan_batch
from src.candle_session import ensure_ordered_session
from src.scan_store import ScanStore
from src.universe_research import validate_dates

IST=ZoneInfo("Asia/Kolkata")

def process_once(token,security_id,symbol,now,store,*,fetch=fetch_intraday,
                 expected_bars=72,latest_allowed_delay_minutes=10,reference_dates=None):
    if now.tzinfo is None:raise ValueError("Clock requires timezone")
    local=now.astimezone(IST)
    if reference_dates is None:
        return {"status":"REFERENCE_DATES_REQUIRED","execution_enabled":False}
    try:
        validate_dates(reference_dates,local.date().isoformat())
    except (ValueError,TypeError):
        return {"status":"INVALID_REFERENCE_DATES","execution_enabled":False}
    if local.strftime("%H:%M")<"09:45" or local.strftime("%H:%M")>"11:35":
        return {"status":"OUTSIDE_SETUP_WINDOW","execution_enabled":False}
    end=(local+timedelta(days=1)).strftime("%Y-%m-%d 09:15:00")
    start=(local-timedelta(days=50)).strftime("%Y-%m-%d 09:15:00")
    raw=fetch(token,security_id,5,start,end)
    records=normalize_dhan_intraday(raw,as_of=local,timestamps_are_open=True)
    today=local.date().isoformat()
    current=[b for b in records if b.time[:10]==today]
    if not current:return {"status":"CURRENT_CANDLES_UNAVAILABLE","execution_enabled":False}
    ensure_ordered_session([b.time for b in current])
    if current[0].time[11:16]!="09:20":
        return {"status":"INCOMPLETE_OPENING","execution_enabled":False}
    close=datetime.fromisoformat(current[-1].time)
    if not timedelta(0)<=local-close<=timedelta(minutes=latest_allowed_delay_minutes):
        return {"status":"STALE_DATA","execution_enabled":False}
    # Validate exact reference dates; never substitute older days for missing ones.
    hist_payload={key:[raw[key][i] for i,epoch in enumerate(raw["timestamp"])
        if datetime.fromtimestamp(int(epoch),IST).date().isoformat()<today]
        for key in ("timestamp","open","high","low","close","volume")}
    complete,rejected=validated_session_groups(hist_payload,as_of=local,expected_bars=expected_bars)
    by_date={session[0].time[:10]:session for session in complete}
    missing=[day for day in reference_dates if day not in by_date]
    if missing:
        return {"status":"INCOMPLETE_REFERENCE_HISTORY","missing_dates":missing,
                "execution_enabled":False}
    observed={bar.time[:10] for bar in records
              if reference_dates[0]<=bar.time[:10]<today}
    unexpected=sorted(observed-set(reference_dates))
    if unexpected:
        return {"status":"UNEXPECTED_REFERENCE_SESSION","unexpected_dates":unexpected,
                "execution_enabled":False}
    previous=[by_date[day] for day in reference_dates]
    if len(current)>75:raise ValueError("Too many current session candles")
    history_closes=[b.close for session in previous for b in session]
    higher=[b for session in previous for b in aggregate_15m(session)]
    full_15=len(current)//3*3
    if full_15:higher+=aggregate_15m(current[:full_15])
    candidate=CandidateInput(symbol=symbol,completed_5m=current,
        previous_sessions=previous,completed_15m=higher[-150:],
        ema_warmup_closes=history_closes[-200:])
    rows=scan_batch(BatchInput(candidates=[candidate]))
    for row in rows:
        row["mode"]="HISTORICAL_FEED_RESEARCH"
        row["execution_enabled"]=False
        row["chart_reconciled"]=False
        row["reference_dates_matched"]=True
        row["timestamp_verified"]=False
        row["session_classification_verified"]=False
        row["eligibility_verified"]=False
    store.initialize()
    inserted=store.commit_scan(close.isoformat(),rows)
    return {"status":"SCANNED" if inserted else "ALREADY_SCANNED",
            "close":close.isoformat(),"rows":rows if inserted else [],
            "historical_sessions":len(previous),"reference_dates_matched":True,
            "timestamp_verified":False,"session_classification_verified":False,"rejected_historical_days":len(rejected),
            "execution_enabled":False}

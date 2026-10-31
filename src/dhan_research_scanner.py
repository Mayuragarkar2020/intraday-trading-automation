"""Assemble research-only scanner inputs from 21 verified full five-minute sessions.

Derived 15m bars are aggregates of exactly three source 5m bars. Scanner
rejections remain authoritative; this is not permission to trade.
"""
from decimal import Decimal
from src.candle_input import CandleInput,CandidateInput,BatchInput,scan_batch
from src.candle_session import ensure_ordered_session

def aggregate_15m(day):
    ensure_ordered_session([x.time for x in day])
    if day[0].time[11:16]!="09:20" or len(day)%3:
        raise ValueError("Incomplete 15m grouping")
    bars=[]
    for i in range(0,len(day),3):
        group=day[i:i+3]
        bars.append(CandleInput(time=group[-1].time,open=group[0].open,
             high=max(x.high for x in group),low=min(x.low for x in group),
             close=group[-1].close,volume=sum(x.volume for x in group)))
    return bars

def research_snapshot(symbol,sessions,*,at_slot="10:30"):
    if len(sessions)!=21:raise ValueError("Exactly twenty prior and one target session required")
    for day in sessions:
        ensure_ordered_session([x.time for x in day])
        if len(day) not in (72,75) or day[0].time[11:16]!="09:20":
            raise ValueError("Incomplete research session")
    dates=[day[0].time[:10] for day in sessions]
    if dates!=sorted(set(dates)):raise ValueError("Unordered or duplicate sessions")
    target=sessions[-1]
    available=[x for x in target if x.time[11:16]<=at_slot]
    if not available or available[-1].time[11:16]!=at_slot:
        raise ValueError("Requested candle is missing or not aligned")
    history=[x.close for day in sessions[:-1] for x in day]
    aggregated=[x for day in sessions[:-1] for x in aggregate_15m(day)]
    aggregated.extend(aggregate_15m(available[:len(available)//3*3]))
    if len(aggregated)<21:raise ValueError("Insufficient 15m confirmation")
    candidate=CandidateInput(symbol=symbol,completed_5m=available,
        previous_sessions=sessions[:-1],completed_15m=aggregated[-150:],
        ema_warmup_closes=history[-200:])
    result=scan_batch(BatchInput(candidates=[candidate]))[0]
    result["mode"]="HISTORICAL_RESEARCH_ONLY"
    result["execution_enabled"]=False
    result["chart_reconciled"]=False
    return result

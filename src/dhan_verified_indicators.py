"""Read-only indicators from fully verified five-minute Dhan sessions.

Never use partial sessions or manufacture missing candles. Indicator figures
are diagnostics, not trading signals; CAS classification remains external.
"""
from decimal import Decimal
from src.candle_pipeline import ema
from src.session_vwap import session_vwap
from src.candle_session import ensure_ordered_session

D=lambda x:Decimal(str(x))

def calculate_session_indicators(prior_sessions,current_session):
    if len(prior_sessions)<1 or not current_session:
        raise ValueError("Prior sessions and current session required")
    for group in [*prior_sessions,current_session]:
        ensure_ordered_session([x.time for x in group])
        if group[0].time[11:16]!="09:20":
            raise ValueError("Incomplete opening candle")
    history=[x.close for group in prior_sessions for x in group]
    if len(history)<20:
        raise ValueError("Insufficient EMA history")
    closes=history+[x.close for x in current_session]
    e10=ema(closes,10)
    e20=ema(closes,20)
    vwap=session_vwap(current_session)
    # Independent VWAP accounting identity, not an external chart check.
    numerator=sum(((x.high+x.low+x.close)/D(3))*x.volume for x in current_session)
    denominator=sum(x.volume for x in current_session)
    if denominator<=0 or numerator/denominator!=vwap:
        raise ValueError("VWAP reconciliation failed")
    return {"session":current_session[0].time[:10],
            "bars":len(current_session),"ema10":str(e10),"ema20":str(e20),
            "session_vwap":str(vwap),
            "last_close":str(current_session[-1].close),
            "vwap_accounting_verified":True,
            "chart_reconciliation_verified":False,
            "qualified_for_trading":False}

def historical_relative_volume(sessions,current,slot,days=20):
    if len(sessions)<days:raise ValueError("Need 20 prior sessions")
    samples=[]
    for group in sessions[-days:]:
        ensure_ordered_session([x.time for x in group])
        if group[0].time[11:16]!="09:20":raise ValueError("Missing prior opening")
        matches=[x for x in group if x.time[11:16]==slot]
        if len(matches)!=1 or matches[0].volume<=0:raise ValueError("Missing slot")
        samples.append(matches[0].volume)
    match=[x for x in current if x.time[11:16]==slot]
    if len(match)!=1:raise ValueError("Missing current slot")
    return D(match[0].volume)/(D(sum(samples))/D(days))

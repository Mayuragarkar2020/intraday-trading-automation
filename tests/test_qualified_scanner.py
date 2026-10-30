from datetime import date,datetime,timedelta
from decimal import Decimal as D
from zoneinfo import ZoneInfo
from src.candle_pipeline import Candle
from src.qualified_scanner import baseline_for_slot,higher_tf_confirmed,qualify

IST=ZoneInfo("Asia/Kolkata")
def candle(day,hh,mm,price=100,volume=1000):
    t=datetime(day.year,day.month,day.day,hh,mm,tzinfo=IST).isoformat()
    p=D(str(price))
    return Candle(t,p,p+D("0.25"),p-D("0.25"),p,volume)

def past_days(count):
    d=date(2026,10,30);days=[]
    while len(days)<count:
        if d.weekday()<5:days.append(d)
        d-=timedelta(days=1)
    return list(reversed(days))

def test_slot_baseline_exact_twenty_sessions():
    sessions=[[candle(day,9,20,volume=500),candle(day,9,25,volume=600)] for day in past_days(20)]
    assert baseline_for_slot(sessions,"09:25")==D(600)
    try:baseline_for_slot(sessions[:-1],"09:25")
    except ValueError:pass
    else:assert False,"Must refuse incomplete history"

def test_higher_tf_confirmation_and_missing_history():
    days=past_days(2)
    candles=[]
    for i in range(21):
        day=days[i//20]
        minute=i%20
        total=9*60+30+minute*15
        candles.append(candle(day,total//60,total%60,100+i))
    assert higher_tf_confirmed(candles) is True
    assert qualify([],[],[],[]).status=="BLOCK"

def test_fail_closed_when_historical_slots_missing():
    day=date(2026,11,2)
    session=[candle(day,9,20),candle(day,9,25),candle(day,9,30)]
    assert qualify(session,[],[],[D(99)]*20).reason=="INCOMPLETE_OR_INVALID_INDICATOR_DATA"

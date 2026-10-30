from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import pytest
from src.dhan_candle_adapter import normalize_dhan_intraday
IST=ZoneInfo("Asia/Kolkata")
def data():
    t=datetime(2026,11,2,9,15,tzinfo=IST)
    return {"timestamp":[int((t+timedelta(minutes=5*i)).timestamp()) for i in range(3)],
            "open":[100,101,102],"high":[102,103,104],
            "low":[99,100,101],"close":[101,102,103],"volume":[1200,1500,1700]}
def test_normalize_requires_explicit_timestamp_policy():
    with pytest.raises(ValueError,match="unverified"):
        normalize_dhan_intraday(data(),as_of=datetime(2026,11,2,9,31,tzinfo=IST))
def test_dhan_start_times_converted_to_close_and_incomplete_dropped():
    bars=normalize_dhan_intraday(data(),as_of=datetime(2026,11,2,9,26,tzinfo=IST),timestamps_are_open=True)
    assert [x.time[11:16] for x in bars]==["09:20","09:25"]
    assert bars[0].volume==1200
def test_dhan_fails_on_misaligned_arrays_and_duplicate_times():
    d=data();d["volume"]=[123]
    with pytest.raises(ValueError):normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True)
    d=data();d["timestamp"][1]=d["timestamp"][0]
    with pytest.raises(ValueError):normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True)
def test_invalid_prices_are_blocked():
    d=data();d["low"][0]=105
    with pytest.raises(ValueError):normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True)

def test_numeric_epoch_float_and_numeric_string():
    d=data()
    d["timestamp"]=[float(x) for x in d["timestamp"]]
    bars=normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True)
    assert len(bars)==3
    d["timestamp"]=[str(int(x)) for x in d["timestamp"]]
    assert len(normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True))==3

def test_invalid_epoch_units_rejected():
    d=data()
    d["timestamp"][0]*=1000
    with pytest.raises(ValueError,match="Invalid epoch"):
        normalize_dhan_intraday(d,as_of=datetime(2026,11,2,10,0,tzinfo=IST),timestamps_are_open=True)

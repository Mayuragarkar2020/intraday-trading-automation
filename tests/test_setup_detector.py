from decimal import Decimal as D
from src.setup_detector import Bar,detect_setup,confirm_breakout

def bar(i,close="101",high="102",low="100",rv="1.5",htf=True):
    return Bar(str(i),D("101"),D(high),D(low),D(close),1000,
               D("99"),D("98"),D("97"),D(rv),htf)

def test_armed_three_candle_range():
    s=detect_setup([bar(1),bar(2),bar(3)])
    assert s.status=="ARMED"
    assert s.trigger==D("102.05")
    assert s.initial_stop==D("99.95")
    assert confirm_breakout(s,bar(4,high="103",low="100"))=="BREAKOUT_TRIGGERED"

def test_range_not_premature():
    assert detect_setup([bar(1),bar(2)]).status=="WAIT"

def test_higher_tf_blocks():
    assert detect_setup([bar(1),bar(2),bar(3,htf=False)]).reason=="HIGHER_TIMEFRAME_NOT_BULLISH"

def test_low_volume_blocks():
    assert detect_setup([bar(1),bar(2),bar(3,rv="0.8")]).reason=="RELATIVE_VOLUME_INSUFFICIENT"

def test_stop_touch_invalidates_breakout():
    s=detect_setup([bar(1),bar(2),bar(3)])
    assert confirm_breakout(s,bar(4,low="99",high="103"))=="INVALIDATED_STOP_TOUCHED"

def test_below_vwap_blocks():
    x=bar(3,close="96")
    assert detect_setup([bar(1),bar(2),x]).reason=="PRICE_NOT_ABOVE_TRENDS"

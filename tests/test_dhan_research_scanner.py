from datetime import datetime,timedelta
from decimal import Decimal
from src.candle_input import CandleInput
from src.dhan_research_scanner import aggregate_15m,research_snapshot

def day(date):
    t=datetime.fromisoformat(date+"T09:20:00+05:30")
    return [CandleInput(time=(t+timedelta(minutes=5*i)).isoformat(),
        open=Decimal("100"),high=Decimal("101"),low=Decimal("99"),
        close=Decimal("100"),volume=1000) for i in range(72)]
def test_aggregation_preserves_close_and_volume():
    bars=aggregate_15m(day("2026-10-29"))
    assert len(bars)==24
    assert bars[0].time[11:16]=="09:30"
    assert bars[0].volume==3000
def test_research_snapshot_remains_nontrading():
    from datetime import date
    start=date(2026,9,29)
    days=[(start+timedelta(days=i)).isoformat() for i in range(32)
          if (start+timedelta(days=i)).weekday()<5][:21]
    report=research_snapshot("RELIANCE",[day(d) for d in days],at_slot="10:30")
    assert report["execution_enabled"] is False
    assert report["mode"]=="HISTORICAL_RESEARCH_ONLY"
    assert report["status"] in ("BLOCK","FORMING","ARMED","WAIT")

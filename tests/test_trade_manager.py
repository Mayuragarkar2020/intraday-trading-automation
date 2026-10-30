from decimal import Decimal
from src.trade_manager import open_long,on_completed_candle,excursion

def test_mfe_mae_and_breakeven_signal():
    t=open_long("100","98",100,"0.10")
    t,action=on_completed_candle(t,"103","99","102.5","101")
    assert action=="REQUEST_STOP_TO_COST_BREAKEVEN"
    assert excursion(t)["mfe_r"]==Decimal("1.5")
    assert excursion(t)["mae_r"]==Decimal("0.5")
    assert excursion(t)["breakeven_stop_requested"]==Decimal("100.10")

def test_ema_exit_on_completed_close():
    t=open_long(100,98,100,"0.1")
    t,action=on_completed_candle(t,102,99,100,101)
    assert action=="REQUEST_EXIT_EMA10_CLOSE"

def test_protective_stop_requires_broker_reconciliation():
    t=open_long(100,98,100,0)
    t,action=on_completed_candle(t,102,97,101,99)
    assert action=="RECONCILE_STOP_EXECUTION"

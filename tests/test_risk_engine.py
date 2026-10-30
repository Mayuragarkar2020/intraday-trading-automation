from decimal import Decimal
import pytest
from src.risk_engine import size_long

def test_risk_includes_costs():
    r=size_long("1000","990","2")
    assert r.quantity==816
    assert r.total_planned_risk==Decimal("9792")
    assert r.total_planned_risk<=Decimal("9800")
    assert r.gross_exposure<=Decimal("980000")

def test_cash_cap_lowers_quantity():
    r=size_long("4000","3995","1")
    assert r.quantity==245
    assert r.gross_exposure==Decimal("980000")
    assert r.total_planned_risk<=Decimal("9800")

def test_prevent_second_trade():
    r=size_long("1000","990","2",completed_trades_today=1)
    assert r.quantity==0
    assert r.status=="BLOCK_DAILY_TRADE_LIMIT"

def test_invalid_stops_and_costs():
    with pytest.raises(ValueError):size_long("1000","1000","2")
    with pytest.raises(ValueError):size_long("1000","990","-1")

def test_very_wide_stop_blocks_trade():
    r=size_long("10000","1","0")
    assert r.quantity==0
    assert r.status=="BLOCK_INSUFFICIENT_CAPITAL_OR_RISK"

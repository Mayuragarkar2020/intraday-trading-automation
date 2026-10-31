from copy import deepcopy
from datetime import datetime
from decimal import Decimal as D
import pytest
from src.paper_engine import replay
from src.paper_models import ReplayRequest
from src.paper_scenarios import example_request,scenario_suite

NOW=datetime.fromisoformat("2026-10-31T12:00:00+05:30")

def run(data=None):return replay(ReplayRequest.model_validate(data or example_request()),as_of=NOW)

def test_scenario_matrix_passes():
    suite=scenario_suite()
    assert suite["passed"]==suite["total"]==14
    assert all(row["passed"] for row in suite["scenarios"])

def test_deterministic_replay_and_no_input_mutation():
    data=example_request();before=deepcopy(data)
    first=run(data)
    assert first==run(data) and data==before
    data["slippage_bps"]="6"
    assert run(data)["run_id"]!=first["run_id"]

def test_cash_and_costs_reconcile_to_completed_trade():
    result=run();fills=[e for e in result["events"] if e["kind"] in ("ENTRY_FILL","EXIT_FILL")]
    entry=next(e for e in fills if e["kind"]=="ENTRY_FILL")
    exits=[e for e in fills if e["kind"]=="EXIT_FILL"]
    net=sum(D(e["price"])*e["quantity"]-D(e["fee"]) for e in exits)-D(entry["price"])*entry["quantity"]-D(entry["fee"])
    assert D(result["summary"]["net_realized_pnl"])==net
    assert D(result["summary"]["cash"])==D(980000)+net
    assert D(result["trades"][0]["planned_risk"])<=D(9800)
    assert D(entry["price"])*entry["quantity"]+D(entry["fee"])<=D(980000)

def test_next_open_ema_exit_and_next_bar_stop_change():
    result=run();events=result["events"]
    change=next(e for e in events if e["kind"]=="STOP_CHANGED")
    assert change["bar_close"].endswith("09:55:00+05:30") and change["effective"]=="NEXT_BAR"
    assert result["trades"][0]["exit_bar_close"].endswith("10:05:00+05:30")
    assert D(result["trades"][0]["exit_average"])<D(511)

def test_entry_bar_does_not_activate_stop_using_preentry_high():
    data=example_request();data["plans"][0]["bars"]=data["plans"][0]["bars"][:1]
    data["plans"][0]["bars"][0]["high"]=550
    result=run(data)
    assert not any(e["kind"]=="STOP_CHANGED" for e in result["events"])
    assert result["summary"]["open_positions"]==1

def test_stop_beats_ema_and_breakeven_on_ambiguous_bar():
    data=example_request();data["plans"][0]["bars"][1].update(open=503,high=550,low=485,close=489,ema10=500)
    result=run(data)
    assert result["trades"][0]["exit_reason"]=="STOP"
    assert not any(e["kind"]=="STOP_CHANGED" for e in result["events"])

def test_gap_loss_may_exceed_budget_and_is_flagged():
    data=example_request();data["plans"][0]["bars"][1].update(open=470,high=480,low=460,close=475)
    result=run(data)
    assert D(result["trades"][0]["exit_average"])<D(470)
    assert result["summary"]["risk_breaches"]==1

def test_rejected_exit_retries_next_open_and_does_not_fake_fill():
    data=example_request();plan=data["plans"][0]
    plan["bars"][1].update(low=480,reject_exit=True)
    result=run(data)
    assert any(e["kind"]=="EXIT_UNFILLED" for e in result["events"])
    assert result["trades"][0]["exit_bar_close"].endswith("10:00:00+05:30")
    assert result["trades"][0]["exit_reason"]=="STOP"

def test_exit_partial_fills_reconcile_and_never_exceed_volume_cap():
    data=example_request();plan=data["plans"][0]
    plan["bars"][1].update(low=480,volume=100)
    result=run(data)
    exits=[e for e in result["events"] if e["kind"]=="EXIT_FILL"]
    assert len(exits)==2 and exits[0]["quantity"]==1
    assert exits[0]["timing"]=="STOP_WITHIN_BAR" and exits[1]["timing"]=="NEXT_OPEN"
    assert sum(e["quantity"] for e in exits)==result["trades"][0]["quantity"]
    assert result["summary"]["open_positions"]==0

def test_unfilled_exit_keeps_open_position_and_reserved_cash():
    data=example_request()
    for b in data["plans"][0]["bars"][1:]:b.update(can_fill=False)
    result=run(data)
    assert not result["summary"]["complete"] and result["open_position"]["remaining"]>0
    assert result["summary"]["closed_trades"]==0 and D(result["summary"]["cash"])<D(980000)

def test_partial_exit_realized_and_remaining_mark_reconcile_to_equity():
    data=example_request();plan=data["plans"][0]
    plan["bars"]=plan["bars"][:2]
    plan["bars"][1].update(low=480,volume=100)
    result=run(data);summary=result["summary"]
    assert summary["closed_trades"]==0 and summary["open_positions"]==1
    assert D(summary["net_realized_pnl"])<0 and D(summary["closed_trade_net_pnl"])==0
    assert D(summary["ending_equity_estimate"])==D(980000)+D(summary["net_realized_pnl"])+D(summary["unrealized_pnl_estimate"])

def test_force_exit_is_next_open_at_declared_time():
    data=example_request();data["force_exit"]="09:55";data["entry_end"]="09:50"
    result=run(data)
    assert result["trades"][0]["exit_reason"]=="SESSION_FLATTEN"
    assert result["trades"][0]["exit_bar_close"].endswith("10:00:00+05:30")

def test_trade_window_boundary_and_one_daily_fill_including_partial():
    data=example_request();data["entry_start"]="09:50"
    result=run(data)
    fill=next(e for e in result["events"] if e["kind"]=="ENTRY_FILL")
    assert fill["bar_close"].endswith("09:55:00+05:30")
    data["entry_end"]="09:50";data["entry_start"]="09:45"
    assert run(data)["summary"]["entries"]==1
    data["plans"][0]["bars"][0].update(high=499,close=499)
    assert run(data)["summary"]["entries"]==0

@pytest.mark.parametrize("band",[2,5])
def test_low_band_blocks_entry(band):
    data=example_request();data["plans"][0]["price_band"]=band
    assert run(data)["orders"][0]["reason"]=="LOW_PRICE_BAND"

@pytest.mark.parametrize("status",["HOLD","EXCLUDED","UNKNOWN"])
def test_unverified_or_restricted_reference_blocks_entry(status):
    data=example_request();data["plans"][0]["reference_status"]=status
    assert run(data)["summary"]["entries"]==0

@pytest.mark.parametrize("mutation",["missing","duplicate","out_of_order","future","same_bar","bad_ohlc","weekend","cross_session","duplicate_plan","bad_window","no_timezone","holiday"])
def test_invalid_market_data_fails_closed(mutation):
    data=example_request();p=data["plans"][0]
    if mutation=="missing":p["bars"].pop(1)
    elif mutation=="duplicate":p["bars"].insert(1,deepcopy(p["bars"][0]))
    elif mutation=="out_of_order":p["bars"].reverse()
    elif mutation=="future":p["bars"][-1]["time"]="2026-11-02T10:05:00+05:30"
    elif mutation=="same_bar":p["bars"][0]["time"]=p["known_at"]
    elif mutation=="bad_ohlc":p["bars"][0]["open"]=600
    elif mutation=="weekend":p["known_at"]="2026-10-31T09:45:00+05:30"
    elif mutation=="cross_session":p["bars"][-1]["time"]="2026-10-29T10:05:00+05:30"
    elif mutation=="duplicate_plan":data["plans"].append(deepcopy(p))
    elif mutation=="bad_window":data["entry_end"]="09:40"
    elif mutation=="no_timezone":p["known_at"]="2026-10-30T09:45:00"
    elif mutation=="holiday":p["known_at"]="2026-10-20T09:45:00+05:30"
    with pytest.raises(ValueError):run(data)

@pytest.mark.parametrize("value",["NaN","Infinity","1e100000","-1"])
def test_nonfinite_or_unbounded_prices_rejected(value):
    data=example_request();data["plans"][0]["bars"][0]["close"]=value
    with pytest.raises(ValueError):run(data)

def test_no_silent_policy_override():
    data=example_request();data["max_trades_per_day"]=99
    with pytest.raises(ValueError):run(data)

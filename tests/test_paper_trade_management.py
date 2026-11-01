from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from uuid import uuid4
import os

import pytest

from src.forward_paper_ledger import ForwardPaperLedger
from src.paper_entry_selection import reserve_paper_entry
from src.paper_trade_management import simulate_paper_bar
from tests.test_paper_entry_selection import batch


def bar(clock="10:00", **changes):
    return dict(at=f"2026-11-02T{clock}:10+05:30",close_at=f"2026-11-02T{clock}:00+05:30",
        symbol="BBB",security_id="2",universe_revision="b"*64,source_sha256="c"*64,
        close="1000",high="1001",low="999",ema10="999",volume=1000000,
        participation_pct="1",slippage_bps="0",tick_size="0.05",
        timestamp_verified=True,session_contract_verified=True,reference_prices_verified=True,
        breakout_receipts_verified=True,**changes)


@pytest.fixture
def ledger(tmp_path):
    value = ForwardPaperLedger("sqlite:///"+str(tmp_path/"manager.db"))
    reserve_paper_entry(value,"account",batch())
    return value


def send(ledger, clock="10:00", **changes):
    value=bar(clock);value.update(changes)
    return simulate_paper_bar(ledger,"account",value)


def test_reserved_entry_fills_prospectively_and_retry_survives_restart(ledger):
    result=send(ledger)
    assert result["state"]["position"]["quantity"] > 0
    assert result["state"]["fills"][0]["at"].endswith("10:00:10+05:30")
    restarted=ForwardPaperLedger(ledger.database_url)
    assert send(restarted)["status"] == "ALREADY_APPLIED"
    assert restarted.audit("account")["event_count"] == 2


def test_ema_exit_before_1_5r_requires_a_future_receipt(ledger):
    send(ledger)
    result=send(ledger,"10:05",ema10="1001")
    assert result["state"]["position"]
    order=next(o for o in result["state"]["orders"].values() if o["side"]=="SELL")
    assert order["reason"] == "EMA10" and order["status"] == "PENDING"
    assert send(ledger,"10:10")["state"]["position"] is None
    ledger.audit("account")


def test_breakeven_stop_persists_and_initial_stop_stays_immutable(ledger):
    send(ledger)
    state=send(ledger,"10:05",high="1016",close="1015")["state"]
    assert state["position"]["stop"] == "1001"
    assert state["orders"][state["position"]["entry_order_id"]]["stop"] == "990"
    restarted=ForwardPaperLedger(ledger.database_url)
    state=send(restarted,"10:10",low="1000")["state"]
    assert next(o for o in state["orders"].values() if o["side"]=="SELL")["reason"] == "STOP"
    restarted.audit("account")


def test_rejected_stop_change_preserves_initial_stop(ledger):
    send(ledger)
    state=send(ledger,"10:05",high="1016",reject_stop_change=True)["state"]
    assert state["position"]["stop"] == "990"


def test_clock_without_feed_requests_flatten_and_records_deadline_breach(ledger):
    send(ledger)
    ledger.apply("account","clock1",dict(kind="PAPER_CLOCK",at="2026-11-02T14:50:00+05:30"))
    state=ledger.apply("account","clock2",dict(kind="PAPER_CLOCK",at="2026-11-02T15:00:00+05:30"))["state"]
    assert state["position"] and state["management"]["closure_deadline_breached"]
    assert len(state["fills"]) == 1
    ledger.audit("account")


def test_early_flatten_and_late_recovery_keep_breach(ledger):
    send(ledger)
    ledger.apply("account","clock",dict(kind="PAPER_CLOCK",at="2026-11-02T14:50:00+05:30"))
    # First observation after the gap cannot retrospectively fill the request.
    assert send(ledger,"14:55")["state"]["position"]
    assert send(ledger,"15:00",reject_exit=True)["state"]["position"]
    state=send(ledger,"15:05")["state"]
    assert state["position"] is None and state["management"]["closure_deadline_breached"]
    ledger.audit("account")


def test_partial_ioc_entry_and_partial_exit_reconcile(ledger):
    assert send(ledger,volume=1000)["state"]["position"]["quantity"] == 10
    send(ledger,"10:05",ema10="1001")
    state=send(ledger,"10:10",volume=100)["state"]
    assert state["position"]["quantity"] == 9
    assert send(ledger,"10:15")["state"]["position"] is None
    ledger.audit("account")


def test_unverified_bar_does_not_touch_database():
    class NoDatabase:
        def apply(self,*args): raise AssertionError("Database touched")
    value=bar();value["timestamp_verified"]=False
    assert simulate_paper_bar(NoDatabase(),"account",value)["status"]=="HELD_SOURCE_VERIFICATION"


@pytest.mark.parametrize("changes",[
    {"security_id":"3"},{"universe_revision":"d"*64},
    {"at":"2026-11-02T10:02:00+05:30"}, {"at":"2026-11-02T09:59:59+05:30"},
    {"close_at":"2026-11-02T10:01:00+05:30"}, {"low":"1002"}])
def test_bad_source_clock_and_identity_cannot_mutate_account(ledger,changes):
    before=deepcopy(ledger.read("account"))
    with pytest.raises(ValueError): send(ledger,**changes)
    assert ledger.read("account") == before


def test_duplicate_concurrent_workers_apply_one_bar(ledger):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:send(ledger),range(4)))
    assert sum(r["status"]=="APPLIED" for r in results)==1
    assert ledger.audit("account")["event_count"]==2


def test_conflicting_retry_rolls_back(ledger):
    send(ledger)
    with pytest.raises(ValueError,match="conflict"): send(ledger,volume=100)
    assert ledger.audit("account")["event_count"]==2


def test_expired_pending_entry_can_be_cancelled_without_a_fill(ledger):
    state=ledger.apply("account","clock",dict(kind="PAPER_CLOCK",at="2026-11-02T11:30:00+05:30"))["state"]
    assert not state["position"] and not state["fills"]
    assert all(o["status"]=="IOC_CANCELLED" for o in state["orders"].values())
    ledger.audit("account")


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"),reason="PostgreSQL CI only")
def test_postgres_manager_concurrency_and_restart():
    backend=ForwardPaperLedger(os.environ["TEST_UNIVERSE_DATABASE_URL"])
    account="manager_"+uuid4().hex
    reserve_paper_entry(backend,account,batch())
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:simulate_paper_bar(backend,account,bar()),range(4)))
    assert sum(r["status"]=="APPLIED" for r in results)==1
    restarted=ForwardPaperLedger(backend.database_url)
    assert simulate_paper_bar(restarted,account,bar())["status"]=="ALREADY_APPLIED"
    assert restarted.audit(account)["event_count"]==2

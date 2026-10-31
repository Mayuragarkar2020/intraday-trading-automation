from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from decimal import Decimal
import os
from uuid import uuid4

import pytest

from src.forward_paper_ledger import ForwardPaperLedger, initial_state, transition


def at(clock="09:45:10", day="2026-11-02"):
    return day+"T"+clock+"+05:30"


def entry(**changes):
    return {"kind": "ENTRY_REQUEST", "at": at(), "order_id": "entry1",
            "signal_id": "signal1", "universe_revision": "revision1",
            "source_sha256": "a"*64, "known_at": at("09:45:00"),
            "quantity": 100, "limit": "100", "stop": "95", "fee_budget": "20", **changes}


def filled(**changes):
    return {"kind": "ENTRY_RESULT", "at": at("09:50:10"), "order_id": "entry1",
            "bar_open_at": at("09:50:00"), "quantity": 60, "price": "99", "fee": "6", **changes}


def exit_request(**changes):
    return {"kind": "EXIT_REQUEST", "at": at("10:00:00"), "order_id": "exit1",
            "reason": "STOP", **changes}


def exited(**changes):
    return {"kind": "EXIT_RESULT", "at": at("10:00:10"), "order_id": "exit1",
            "quantity": 20, "price": "90", "fee": "2", **changes}


@pytest.fixture
def ledger(tmp_path):
    return ForwardPaperLedger("sqlite:///"+str(tmp_path/"ledger.db"))


def open_position(ledger, account="test"):
    ledger.apply(account, "request", entry())
    return ledger.apply(account, "fill", filled())["state"]


def test_partial_ioc_and_partial_stop_exit_reconcile_across_restart(ledger):
    state = open_position(ledger)
    assert state["cash"] == "974054"
    assert state["orders"]["entry1"]["status"] == "IOC_CANCELLED"
    assert state["position"]["quantity"] == 60
    ledger.apply("test", "exit_request", exit_request())
    state = ledger.apply("test", "exit_partial", exited())["state"]
    assert state["position"]["quantity"] == 40
    assert state["orders"]["exit1"]["status"] == "PENDING"
    assert Decimal(state["realised_pnl"]) == -184
    restarted = ForwardPaperLedger(ledger.database_url)
    assert restarted.read("test") == state
    final = restarted.apply("test", "exit_final", exited(quantity=40, fee="4", at=at("10:05:00")))["state"]
    assert final["position"] is None
    assert Decimal(final["cash"]) == Decimal("980000") + Decimal(final["realised_pnl"])
    assert final["fees"] == "12"
    assert final["used_entry_dates"] == ["2026-11-02"]
    assert restarted.audit("test")["event_count"] == 5


def test_retry_returns_original_result_even_after_newer_events(ledger):
    first = ledger.apply("test", "request", entry())["state"]
    ledger.apply("test", "fill", filled())
    retry = ledger.apply("test", "request", entry())
    assert retry == {"status": "ALREADY_APPLIED", "state": first}
    assert ledger.read("test")["position"]["quantity"] == 60
    with pytest.raises(ValueError, match="identity conflict"):
        ledger.apply("test", "request", entry(quantity=99))


def test_duplicate_concurrent_ticks_only_apply_once(ledger):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: ledger.apply("test", "request", entry()), range(4)))
    assert sum(r["status"] == "APPLIED" for r in results) == 1
    assert ledger.audit("test")["event_count"] == 1


def test_competing_workers_cannot_create_two_pending_entries(ledger):
    def submit(i):
        try:
            return ledger.apply("test", "request"+str(i), entry(order_id="order"+str(i)))
        except ValueError:
            return None
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(submit, range(4)))
    assert sum(r is not None for r in results) == 1
    assert ledger.audit("test")["event_count"] == 1


@pytest.mark.parametrize("change", [
    {"quantity": True}, {"quantity": -1}, {"quantity": 0}, {"quantity": 1000001},
    {"quantity": 10000}, {"stop": "101"}, {"limit": "NaN"}, {"limit": 100},
    {"fee_budget": "-1"}, {"source_sha256": "invalid"}, {"unknown": 1},
    {"known_at": at("09:46:00")}, {"known_at": "2026-11-02T09:45:00"},
    {"at": at("09:44:59")}, {"at": at("11:30:01")},
    {"known_at": at(day="2026-11-01")},
])
def test_invalid_entry_fails_without_creating_account(ledger, change):
    with pytest.raises((ValueError, TypeError)):
        ledger.apply("test", "bad", entry(**change))
    assert ledger.read("test") is None


@pytest.mark.parametrize("change", [
    {"bar_open_at": at("09:45:00")}, {"bar_open_at": at("09:45:05")},
    {"bar_open_at": at("09:55:00")}, {"bar_open_at": at(day="2026-11-03")},
    {"quantity": 101}, {"quantity": 0}, {"price": "101"}, {"price": "94"},
    {"fee": "21"}, {"at": at("09:44:00")},
])
def test_invalid_entry_fill_rolls_back(ledger, change):
    original = ledger.apply("test", "request", entry())["state"]
    with pytest.raises(ValueError):
        ledger.apply("test", "bad", filled(**change))
    assert ledger.read("test") == original
    assert ledger.audit("test")["event_count"] == 1


def test_rejected_entry_is_flat_and_does_not_consume_daily_fill(ledger):
    ledger.apply("test", "request", entry())
    state = ledger.apply("test", "reject", filled(quantity=0, price="0", fee="0"))["state"]
    assert state["position"] is None and not state["used_entry_dates"]
    ledger.apply("test", "retry_new_signal", entry(order_id="entry2", signal_id="signal2", at=at("09:55:00")))
    assert ledger.audit("test")["event_count"] == 3


def test_unfilled_exit_preserves_exposure_and_prevents_second_exit(ledger):
    open_position(ledger)
    ledger.apply("test", "exit_request", exit_request(reason="FLATTEN"))
    state = ledger.apply("test", "rejected_exit", exited(quantity=0, price="0", fee="0"))["state"]
    assert state["position"]["quantity"] == 60
    assert state["orders"]["exit1"]["status"] == "PENDING"
    with pytest.raises(ValueError):
        ledger.apply("test", "duplicate_exit", exit_request(order_id="exit2", at=at("10:05:00")))
    with pytest.raises(ValueError):
        ledger.apply("test", "oversell", exited(quantity=61))
    assert ledger.read("test") == state


def test_flat_account_still_remembers_filled_daily_entry(ledger):
    open_position(ledger)
    ledger.apply("test", "exit_request", exit_request())
    ledger.apply("test", "exit_fill", exited(quantity=60))
    with pytest.raises(ValueError, match="Daily filled"):
        ledger.apply("test", "another", entry(order_id="another", at=at("10:05:00")))
    ledger.apply("test", "tomorrow", entry(order_id="tomorrow", signal_id="tomorrow",
                 at=at(day="2026-11-03"), known_at=at("09:45:00", day="2026-11-03")))


def test_crash_after_journal_insert_rolls_back_entire_transaction(ledger):
    ledger.initialize()
    with ledger.connection() as db:
        db.execute("""CREATE TRIGGER fail_projection BEFORE INSERT ON forward_paper_accounts
                      BEGIN SELECT RAISE(ABORT, 'injected failure'); END""")
    with pytest.raises(Exception, match="injected failure"):
        ledger.apply("test", "request", entry())
    with ledger.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM forward_paper_events").fetchone()[0] == 0
        db.execute("DROP TRIGGER fail_projection")
    assert ledger.apply("test", "request", entry())["status"] == "APPLIED"


def test_audit_detects_corrupted_projection(ledger):
    open_position(ledger)
    with ledger.connection() as db:
        db.execute("UPDATE forward_paper_accounts SET payload='{}'")
    with pytest.raises(ValueError, match="reconciliation"):
        ledger.audit("test")


def test_failed_pure_transition_never_mutates_input():
    state = transition(initial_state(), entry())
    before = deepcopy(state)
    with pytest.raises(ValueError):
        transition(state, filled(quantity=1000))
    assert state == before


def test_database_failure_is_not_success(tmp_path):
    backend = ForwardPaperLedger("sqlite:///"+str(tmp_path/"missing"/"ledger.db"))
    with pytest.raises(Exception):
        backend.apply("test", "request", entry())


def test_rejected_signal_cannot_be_rebound_to_another_order(ledger):
    ledger.apply("test", "request", entry())
    ledger.apply("test", "reject", filled(quantity=0, price="0", fee="0"))
    with pytest.raises(ValueError, match="Signal already bound"):
        ledger.apply("test", "rebind", entry(order_id="entry2", at=at("09:55:00")))


def test_fractional_entry_fee_allocation_reconciles_on_final_exit(ledger):
    ledger.apply("test", "request", entry(quantity=3))
    ledger.apply("test", "fill", filled(quantity=3, fee="1"))
    ledger.apply("test", "exit_request", exit_request())
    ledger.apply("test", "partial", exited(quantity=1, price="101", fee="0.1"))
    final = ledger.apply("test", "remaining", exited(quantity=2, price="101", fee="0.2"))["state"]
    assert Decimal(final["cash"]) - Decimal("980000") == Decimal(final["realised_pnl"])
    assert ledger.audit("test")["event_count"] == 5


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"), reason="PostgreSQL CI only")
def test_postgres_concurrent_fills_and_restart():
    backend = ForwardPaperLedger(os.environ["TEST_UNIVERSE_DATABASE_URL"])
    account = "ledger_"+uuid4().hex
    backend.apply(account, "request", entry())
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: backend.apply(account, "fill", filled()), range(4)))
    assert sum(r["status"] == "APPLIED" for r in results) == 1
    restarted = ForwardPaperLedger(backend.database_url)
    assert restarted.read(account)["position"]["quantity"] == 60
    assert restarted.audit(account)["event_count"] == 2


from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from decimal import Decimal
import os
from uuid import uuid4

import pytest

from src.forward_paper_ledger import ForwardPaperLedger
from src.paper_entry_selection import EntryBatch, reserve_paper_entry


def batch():
    def candidate(symbol, sid, score):
        return dict(symbol=symbol, security_id=sid, signal_id=sid.zfill(64),
                    source_sha256="a"*64, universe_revision="b"*64,
                    status="BREAKOUT_CONFIRMED", setup_known_at="2026-11-02T09:44:00+05:30",
                    breakout_observed_at="2026-11-02T09:47:00+05:30",
                    avg_turnover_20d_cr=score, entry_limit="1000", initial_stop="990")
    return dict(batch_id="cycle1", interval_start="2026-11-02T09:45:00+05:30",
                decision_at="2026-11-02T09:50:10+05:30", round_trip_cost_per_share="1",
                timestamp_verified=True, session_contract_verified=True,
                reference_prices_verified=True, breakout_receipts_verified=True,
                candidates=[candidate("AAA", "1", "100"), candidate("BBB", "2", "200")])


@pytest.fixture
def ledger(tmp_path):
    return ForwardPaperLedger("sqlite:///"+str(tmp_path/"selection.db"))


def test_ranking_reserves_without_filling_and_persists_evidence(ledger):
    result=reserve_paper_entry(ledger,"test",batch())
    assert result["status"]=="RESERVED"
    command=result["command"]
    assert command["symbol"]=="BBB"
    assert command["quantity"]==890  # risk includes estimated costs
    assert command["known_at"]==command["at"]==batch()["decision_at"]
    assert command["selection"]["policy"]=="LIQUIDITY_20D_V1"
    assert [r["symbol"] for r in command["selection"]["ranking"]]==["BBB","AAA"]
    state=ledger.read("test")
    assert state["cash"]=="980000" and state["position"] is None
    assert ledger.event("test",command["order_id"])["command"]==command
    assert not result["execution_enabled"] and not result["paper_runtime_enabled"]


def test_equivalent_retry_and_conflicting_batch(ledger):
    first=reserve_paper_entry(ledger,"test",batch())
    retry=batch()
    retry["candidates"].reverse()
    retry["candidates"][0]["avg_turnover_20d_cr"]="200.0"
    assert reserve_paper_entry(ledger,"test",retry)["command"]==first["command"]
    retry["candidates"][0]["entry_limit"]="1001"
    with pytest.raises(ValueError,match="Immutable"):
        reserve_paper_entry(ledger,"test",retry)
    assert ledger.audit("test")["event_count"]==1


def test_deterministic_tie(ledger):
    value=batch()
    value["candidates"][0]["avg_turnover_20d_cr"]="200"
    value["candidates"].reverse()
    assert reserve_paper_entry(ledger,"test",value)["command"]["symbol"]=="AAA"


@pytest.mark.parametrize("flag",["timestamp_verified","session_contract_verified",
                                 "reference_prices_verified","breakout_receipts_verified"])
def test_unverified_sources_do_not_touch_database(flag):
    class NoDatabase:
        def initialize(self): raise AssertionError("Database touched")
    value=batch(); value[flag]=False
    assert reserve_paper_entry(NoDatabase(),"test",value)["status"]=="HELD_SOURCE_VERIFICATION"


@pytest.mark.parametrize("change",[
    {"decision_at":"2026-11-02T09:49:59+05:30"},
    {"decision_at":"2026-11-02T09:51:31+05:30"},
    {"interval_start":"2026-11-02T09:46:00+05:30"},
    {"decision_at":"2026-11-02T09:50:10"},
    {"unexpected":True},
])
def test_invalid_batch(change):
    with pytest.raises(ValueError): EntryBatch.model_validate({**batch(),**change})


def test_duplicate_and_mixed_reference_rejected():
    value=batch(); value["candidates"][1]=deepcopy(value["candidates"][0])
    with pytest.raises(ValueError): EntryBatch.model_validate(value)
    value=batch(); value["candidates"][1]["universe_revision"]="c"*64
    with pytest.raises(ValueError): EntryBatch.model_validate(value)


def test_concurrent_same_batch_is_idempotent(ledger):
    ledger.initialize()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:reserve_paper_entry(ledger,"test",batch()),range(4)))
    assert sum(r["status"]=="RESERVED" for r in results)==1
    assert ledger.audit("test")["event_count"]==1


def test_competing_batches_reserve_once(ledger):
    ledger.initialize()
    def submit(i):
        value=batch(); value["batch_id"]="cycle"+str(i)
        return reserve_paper_entry(ledger,"test",value)
    with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(submit,range(4)))
    assert sum(r["status"]=="RESERVED" for r in results)==1
    assert ledger.audit("test")["event_count"]==1


def test_no_backdated_fill_and_retry_after_fill(ledger):
    command=reserve_paper_entry(ledger,"test",batch())["command"]
    fill=dict(kind="ENTRY_RESULT",at="2026-11-02T09:55:10+05:30",order_id=command["order_id"],
              bar_open_at="2026-11-02T09:50:00+05:30",quantity=10,price="1000",fee="1")
    with pytest.raises(ValueError): ledger.apply("test","early",fill)
    fill["bar_open_at"]="2026-11-02T09:55:00+05:30"
    state=ledger.apply("test","fill",fill)["state"]
    assert state["position"]["symbol"]=="BBB" and state["position"]["security_id"]=="2"
    assert reserve_paper_entry(ledger,"test",batch())["command"]==command
    value=batch(); value["batch_id"]="another"
    assert reserve_paper_entry(ledger,"test",value)["status"]=="HELD_ACCOUNT_ENTRY_LIMIT"
    assert Decimal(state["cash"])>=0


def test_selection_and_reservation_roll_back_together(ledger):
    ledger.initialize()
    with ledger.connection() as db:
        db.execute("""CREATE TRIGGER fail_selection BEFORE INSERT ON forward_paper_accounts
                      BEGIN SELECT RAISE(ABORT, 'injected failure'); END""")
    with pytest.raises(Exception,match="injected failure"):
        reserve_paper_entry(ledger,"test",batch())
    with ledger.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM forward_paper_events").fetchone()[0]==0
        db.execute("DROP TRIGGER fail_selection")
    assert reserve_paper_entry(ledger,"test",batch())["status"]=="RESERVED"


@pytest.mark.skipif(not os.getenv("TEST_UNIVERSE_DATABASE_URL"),reason="PostgreSQL CI only")
def test_postgres_selection_concurrency_and_restart():
    backend=ForwardPaperLedger(os.environ["TEST_UNIVERSE_DATABASE_URL"])
    account="selection_"+uuid4().hex
    backend.initialize()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda _:reserve_paper_entry(backend,account,batch()),range(4)))
    assert sum(r["status"]=="RESERVED" for r in results)==1
    restarted=ForwardPaperLedger(backend.database_url)
    assert reserve_paper_entry(restarted,account,batch())["status"]=="ALREADY_RESERVED"
    assert restarted.audit(account)["event_count"]==1


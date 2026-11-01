"""Whole user journey using synthetic future clearances, never market proof."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
import os
import json
from urllib.parse import urlencode
from uuid import uuid4

import pytest
from src.human_paper_controller import HumanPaperController,CommittedPaperSource,FLAGS
from src.paper_choice import ACCOUNT,PaperChoiceStore
from src.paper_trade_journal import trade_journal
from src.universe_scanner import UniverseScanStore,candidate_from,prepare_history,digest
from src.forward_paper_ledger import encode
from src.daily_universe_refresh import reference_dates_for
from src.run_forward_capture import CALENDAR
from tests.test_paper_choice import seed,command
from tests.test_universe_scanner import at


def stamp(clock,seconds=0):return at(clock+f":{seconds:02}")


class FutureFixtureSource(CommittedPaperSource):
    """TEST ONLY. No production producer currently supplies these clearances."""
    def read(self,rid):
        r=super().read(rid)
        if r:r={**r,**{f:True for f in FLAGS}}
        return r
    def reference_cleared(self,r):return True


class Flow:
    def __init__(self,url):
        self.store,ids=seed(url);self.scan=UniverseScanStore(url)
        self.source=FutureFixtureSource(url);self.controller=HumanPaperController(self.source)
        self.revision=self.store.read(ids[0])["universe_revision"]
        self.history=self.scan.reference(self.revision,"100")
        dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
        self.previous=prepare_history(self.history,stamp("09:55"),dates)
        self.overrides={};self.next("09:50");self.next("09:55")
        self.setup=self.source.latest_for("STOCK0","100",self.revision,"2026-11-02")
        p="%s" if self.store.postgres else "?"
        r=deepcopy(self.store.read(self.setup["receipt_id"]))
        r["scanner_result"].update(status="ARMED",entry="1005.05",stop="990")
        with self.store.connection() as db:
            db.execute("UPDATE universe_receipt_signals SET payload="+p+",sha256="+p+" WHERE receipt_id="+p,
                       (encode(r),digest(r),r["receipt_id"]))
        self.scan.save_cycle(dict(cycle_id="d"*64,candle_close=stamp("09:55").isoformat(),
            universe_revision=self.revision,mode="FULL_UNIVERSE_RESEARCH_ONLY",execution_enabled=False,
            forward_paper_ready=False,rows=[dict(symbol="STOCK0",security_id="100",selected=True,
                status="SCANNED",setup_status="ARMED",receipt_id=r["receipt_id"])]))
        self.setup=r
    def choose(self):
        return self.store.choose(command(self.setup["receipt_id"]),stamp("09:55",20))["selected"]
    def raw(self,clock,**changes):
        if changes:self.overrides[clock]=changes
        close=stamp(clock);n=int((close-stamp("09:15")).total_seconds()/300)
        raw={"timestamp":[],"open":[],"high":[],"low":[],"close":[],"volume":[]}
        for i in range(n):
            opened=stamp("09:15")+timedelta(minutes=i*5);closed=opened+timedelta(minutes=5)
            label=closed.strftime("%H:%M")
            values=dict(open=1000,high=1001,low=999,close=1000,volume=1000)
            if label>="10:05":values.update(open=1004.5,high=1007,low=1003,close=1004.5,volume=1000000)
            values.update(self.overrides.get(label,{}))
            raw["timestamp"].append(int(opened.timestamp()))
            for k,v in values.items():raw[k].append(v)
        return raw
    def next(self,clock,**changes):
        raw=self.raw(clock,**changes);close=stamp(clock);observed=close+timedelta(seconds=10)
        c=candidate_from("STOCK0",self.previous,raw,observed,close)
        return self.store.record(self.revision,"100",c,digest(self.history),digest(raw),observed.isoformat(),
                                 clock=lambda:observed+timedelta(seconds=1))["receipt"]
    def run(self,clock):return self.controller.run_once(stamp(clock,20))
    def account(self):
        with self.store.connection() as db:return self.store.account(db)
    def enter(self):
        self.choose();self.next("10:00");assert self.run("10:00")["status"]=="WAIT_FOR_LATER_BREAKOUT"
        self.next("10:05");assert self.run("10:05")["status"]=="ENTRY_RESERVED"
        self.next("10:10");assert self.run("10:10")["status"]=="WAIT_FOR_FULL_POST_DECISION_BAR"
        self.next("10:15");assert self.run("10:15")["status"]=="PAPER_BAR_PROCESSED"
        assert self.account()["position"]


@pytest.fixture(params=["sqlite","postgres"])
def flow(tmp_path,request):
    url="sqlite:///"+str(tmp_path/"flow.db");cleanup=None
    if request.param=="postgres":
        if not os.getenv("TEST_UNIVERSE_DATABASE_URL"):pytest.skip("PostgreSQL CI only")
        import psycopg
        from psycopg import sql
        base=os.environ["TEST_UNIVERSE_DATABASE_URL"];schema="human_flow_"+uuid4().hex
        with psycopg.connect(base) as db:db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        url=base+("&" if '?' in base else '?')+urlencode({"options":"-csearch_path="+schema})
        def cleanup():
            with psycopg.connect(base) as db:db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    try:yield Flow(url)
    finally:
        if cleanup:cleanup()


def test_no_human_choice_means_no_entry_or_account_creation(flow):
    assert flow.run("09:55")["status"]=="NO_STOCK_CHOICE"
    with flow.store.connection() as db:assert not flow.store.table_exists(db,"forward_paper_accounts")


def test_actual_research_clearance_remains_held_even_after_user_choice(flow):
    flow.choose()
    actual=HumanPaperController(CommittedPaperSource(flow.store.database_url))
    assert actual.run_once(stamp("09:55",20))["status"]=="HELD_SOURCE_VERIFICATION"
    with flow.store.connection() as db:assert not flow.store.table_exists(db,"forward_paper_accounts")


def test_one_choice_to_automatic_fill_ema_exit_and_completed_journal(flow):
    flow.enter()
    account=flow.account();assert account["position"]["symbol"]=="STOCK0"
    order=account["orders"][account["position"]["entry_order_id"]]
    assert Decimal(order["quantity"])*(Decimal(order["limit"])-Decimal(order["stop"]))+Decimal(order["fee_budget"])<=9800
    assert Decimal(order["quantity"])*Decimal(order["limit"])+Decimal(order["fee_budget"])<=980000
    flow.next("10:20",low=998,close=999)
    assert flow.run("10:20")["status"]=="PAPER_BAR_PROCESSED"
    assert flow.account()["position"]  # exit request is not a fill
    flow.next("10:25",low=998,close=999)
    result=flow.run("10:25")
    assert flow.account()["position"] is None
    trade=result["journal"]["trades"][0]
    assert trade["choice_id"]==flow.store.workspace(stamp("10:25",20))["selected"]["choice_id"]
    assert trade["exit_reason"]=="EMA10" and trade["initial_stop"]=="990"
    assert trade["entry_at"].endswith("10:15:20+05:30") and trade["exit_at"].endswith("10:25:20+05:30")
    assert Decimal(flow.account()["cash"])==Decimal("980000")+Decimal(trade["net_pnl"])
    assert not trade["closure_deadline_breached"]
    assert flow.controller.ledger.audit(ACCOUNT)["event_count"]>0
    assert flow.run("10:25")["status"]=="DAILY_ENTRY_USED"


def test_duplicate_workers_and_restart_do_not_double_fill(flow):
    flow.enter()
    before=len(flow.account()["fills"])
    fresh=HumanPaperController(FutureFixtureSource(flow.store.database_url))
    assert fresh.run_once(stamp("10:15",25))["ledger_status"]=="ALREADY_APPLIED"
    assert len(flow.account()["fills"])==before
    flow.controller.ledger.audit(ACCOUNT)


def test_cost_breakeven_keeps_initial_stop_and_covers_declared_execution_costs(flow):
    flow.enter();flow.next("10:20",high=1040,close=1030)
    flow.run("10:20");account=flow.account();position=account["position"]
    assert Decimal(position["stop"])>Decimal(position["entry_price"])+1
    assert account["orders"][position["entry_order_id"]]["stop"]=="990"


def test_prospective_flatten_waits_for_later_receipt_then_closes_before_1500(flow):
    flow.enter()
    for clock in ("14:35","14:40","14:45","14:50"):
        flow.next(clock);flow.run(clock)
    assert flow.account()["position"]  # 14:50 clock request cannot fill a 14:50 bar
    flow.next("14:55");flow.run("14:55")
    assert flow.account()["position"] is None
    trade=trade_journal(flow.account())["trades"][0]
    assert trade["exit_reason"]=="FLATTEN" and not trade["closure_deadline_breached"]


def test_missing_feed_does_not_stop_clock_or_erase_deadline_exposure(flow):
    flow.enter()
    flow.run("14:50")  # stale morning receipt; request still persisted
    assert any(o.get("reason")=="FLATTEN" for o in flow.account()["orders"].values())
    flow.run("15:00")
    account=flow.account()
    assert account["position"] and account["management"]["closure_deadline_breached"]
    assert not trade_journal(account)["trades"]


def test_setup_stop_invalidation_prevents_entry(flow):
    flow.choose();flow.next("10:00",low=980)
    assert flow.run("10:00")["status"]=="CHOICE_INVALIDATED_STOP"
    assert flow.account() is None


def test_partial_entry_and_partial_exit_keep_journal_open_until_final_fill(flow):
    flow.choose();flow.next("10:00");flow.run("10:00")
    flow.next("10:05");flow.run("10:05")
    flow.next("10:15",volume=1000);flow.run("10:15")
    assert flow.account()["position"]["quantity"]==10
    flow.next("10:20",low=998,close=999);flow.run("10:20")
    flow.next("10:25",low=998,close=999,volume=100);flow.run("10:25")
    journal=trade_journal(flow.account())
    assert not journal["trades"] and journal["open_trade"]["remaining"]==9
    flow.next("10:30");flow.run("10:30")
    journal=trade_journal(flow.account())
    assert not journal["open_trade"] and journal["trades"][0]["quantity"]==10
    assert Decimal(flow.account()["cash"])==Decimal("980000")+Decimal(journal["trades"][0]["net_pnl"])


def test_zero_volume_exit_stays_pending_then_recovers(flow):
    flow.enter();flow.next("10:20",low=998,close=999);flow.run("10:20")
    flow.next("10:25",low=998,close=999,volume=0);flow.run("10:25")
    assert flow.account()["position"]
    assert flow.store.workspace(stamp("10:25",20))["management_state"]=="EXIT_PENDING"
    flow.next("10:30");flow.run("10:30")
    assert not flow.account()["position"]


def test_disabled_controller_does_not_touch_store_or_sources(monkeypatch):
    from src import human_paper_controller as module
    monkeypatch.delenv("FORWARD_PAPER_ENABLED",raising=False)
    monkeypatch.setattr(module,"CommittedPaperSource",lambda *a:pytest.fail("Store touched"))
    assert module.run_configured_cycle()["status"]=="PAPER_CONTROLLER_DISABLED"


def test_runtime_failure_cannot_report_flat_or_leak_private_details(monkeypatch):
    from src import human_paper_controller as module
    monkeypatch.setenv("FORWARD_PAPER_ENABLED","true")
    monkeypatch.setenv("SCAN_DATABASE_URL","postgresql://private-connection")
    class Failure:
        def __init__(self,*a):pass
        def run_once(self,*a):raise RuntimeError("private-connection")
    from contextlib import contextmanager
    class Empty:
        def __init__(self,*a):pass
        @contextmanager
        def connection(self):yield None
        def account(self,db):return None
        def selected(self,db):return None
    monkeypatch.setattr(module,"CommittedPaperSource",Empty)
    monkeypatch.setattr(module,"HumanPaperController",Failure)
    result=module.run_configured_cycle(clock=lambda:stamp("10:00",20))
    assert result["exposure_status"]=="UNKNOWN" and "private-connection" not in str(result)


def test_single_stock_feed_records_receipt_without_promoting_clearance(flow):
    from src.human_paper_controller import collect_chosen_receipt
    choice=flow.choose();calls=[]
    def fetch(token,sid,interval,start,end):
        calls.append((sid,interval))
        return flow.raw("10:00")
    result=collect_chosen_receipt(flow.store,choice,stamp("10:00",5),"fixture-token",
        fetch=fetch,clock=lambda:stamp("10:00",20))
    assert result["status"]=="RECORDED" and calls==[("100",5)]
    receipt=flow.store.read(result["receipt_id"])
    assert not any(receipt[f] for f in FLAGS)


def test_worker_records_clock_before_feed_failure_and_keeps_exposure(flow,monkeypatch):
    if not flow.store.postgres:pytest.skip("Production worker requires PostgreSQL; exercised in CI")
    from src.human_paper_controller import run_configured_cycle
    import httpx
    flow.enter()
    monkeypatch.setenv("FORWARD_PAPER_ENABLED","true")
    monkeypatch.setenv("SCAN_DATABASE_URL",flow.store.database_url)
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","fixture-token")
    def failure(*args):
        assert any(o.get("reason")=="FLATTEN" for o in flow.account()["orders"].values())
        raise httpx.ReadTimeout("private broker body")
    result=run_configured_cycle(clock=lambda:stamp("14:50",20),fetch=failure)
    assert result["feed_status"]=="HELD_FEED_FAILURE" and flow.account()["position"]
    result=run_configured_cycle(clock=lambda:stamp("15:00",20),fetch=failure)
    assert flow.account()["management"]["closure_deadline_breached"]
    assert "private broker body" not in str(result)


def test_paper_worker_has_priority_over_universe_research_when_opted_in(monkeypatch,capsys):
    from src import run_scheduled_research as scheduled,human_paper_controller as paper,run_universe_research as universe
    calls=[]
    monkeypatch.setenv("FORWARD_PAPER_ENABLED","true")
    monkeypatch.setenv("UNIVERSE_SCAN_ENABLED","true")
    monkeypatch.setattr(paper,"run_configured_cycle",lambda:calls.append("PAPER") or {"status":"HELD_SOURCE_VERIFICATION"})
    monkeypatch.setattr(universe,"main",lambda:calls.append("RESEARCH") or 0)
    assert scheduled.main()==0 and calls==["PAPER","RESEARCH"]
    assert "HELD_SOURCE_VERIFICATION" in capsys.readouterr().out

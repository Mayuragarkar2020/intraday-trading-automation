"""Synthetic future clearances test wiring, never actual source certification."""
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
import hashlib
import json

import pytest

from src.forward_paper_ledger import ForwardPaperLedger, encode
from src.paper_entry_selection import EntryBatch, canonical_batch
from src.persisted_paper_bridge import reserve_from_receipts, manage_from_receipt, FLAGS
from src.universe_receipts import UniverseReceiptStore
from src.universe_scanner import UniverseScanStore, candidate_from, prepare_history, digest
from src.universe_store import UniverseStore
from src.daily_universe_refresh import reference_dates_for
from src.run_forward_capture import CALENDAR
from tests.test_universe_scanner import at, bars
from tests.test_paper_entry_selection import batch


def stamp(clock): return at(clock+":00")


class FutureFixtureStore:
    """TEST ONLY: current producer never writes these clearance flags/mode."""
    def __init__(self,backend): self.backend=backend;self.postgres=False
    def connection(self): return self.backend.connection()
    def read(self,rid):
        r=deepcopy(self.backend.read(rid))
        if r is None:return None
        r.update(**{k:True for k in FLAGS})
        if r["candle_close"][11:16]=="09:55":
            r["scanner_result"].update(status="ARMED",entry="1000",stop="990")
        return r


@pytest.fixture
def evidence(tmp_path):
    url="sqlite:///"+str(tmp_path/"bridge.db")
    universe=UniverseStore(url);universe.initialize()
    snapshot={"mode":"VERIFIED_PAPER_UNIVERSE","target_date":"2026-11-02",
        "asof_date":"2026-10-30","restrictions_verified":True,
        "calendar_completeness_verified":True,"candidates":[
            dict(symbol="STOCK"+str(i),dhan_security_id=str(100+i),liquidity_pass=True,
                 mapping_status="UNIQUE",reference_review_status="VERIFIED",reference_price_band="20",
                 metrics={"avg_turnover_20d_cr":str((i+1)*100)}) for i in range(2)]}
    payload,proof=encode(snapshot),'{}'
    revision=hashlib.sha256((payload+"\n"+proof).encode()).hexdigest()
    with universe.backend.connection() as db:
        db.execute("INSERT INTO universe_research_snapshots VALUES (?,?,?,?,?,?)",
            (revision,"2026-11-02","2026-10-30",at("08:30:00").isoformat(),payload,proof))
    scan=UniverseScanStore(url);scan.initialize()
    store=UniverseReceiptStore(url)
    history=bars(history=True)
    for k,v in (("open",1000),("high",1001),("low",999),("close",1000)):
        history[k]=[v]*len(history[k])
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    previous=prepare_history(history,at(),dates)
    ids={}
    for sid in ("100","101"):
        symbol="STOCK"+str(int(sid)-100)
        scan.save_reference(revision,sid,history)
        for clock in ("09:45","09:50","09:55","10:00","10:05","10:10","10:15","10:20","10:25"):
            close=stamp(clock);observed=close+timedelta(seconds=10)
            n=int((close-stamp("09:15")).total_seconds()/300)
            raw={"timestamp":[int(stamp("09:15").timestamp())+i*300 for i in range(n)],
                "open":[1000]*n,"high":[1001]*n,"low":[999]*n,"close":[1000]*n,"volume":[1000000]*n}
            if clock>="10:20":
                raw["low"][-1]=998;raw["close"][-1]=999
            # Keep earlier source observations immutable when later bars arrive.
            if clock=="10:25":raw["low"][-2]=998;raw["close"][-2]=999
            c=candidate_from(symbol,previous,raw,observed,close)
            r=store.record(revision,sid,c,digest(history),digest(raw),observed.isoformat(),
                           clock=lambda t=observed:t+timedelta(seconds=1))["receipt"]
            ids[(symbol,clock)]=r["receipt_id"]
    return store,FutureFixtureStore(store),ids,ForwardPaperLedger(url)


def pairs(ids):
    return [dict(setup_id=ids[(s,"09:55")],breakout_id=ids[(s,"10:05")]) for s in ("STOCK0","STOCK1")]


def reserve(ledger,store,ids):
    return reserve_from_receipts(ledger,"account",store,pairs(ids),
        decision_at=at("10:05:20").isoformat(),round_trip_cost_per_share="1")


def test_current_real_receipts_do_not_reach_ledger(evidence):
    real,future,ids,ledger=evidence
    class NoLedger:
        def apply(self,*args):raise AssertionError("Ledger touched")
        def initialize(self):raise AssertionError("Ledger touched")
    assert reserve(NoLedger(),real,ids)["status"]=="HELD_SOURCE_VERIFICATION"
    assert manage_from_receipt(NoLedger(),"account",real,ids[("STOCK1","10:15")],
        decision_at=at("10:15:20").isoformat(),participation_pct="1",slippage_bps="0",
        tick_size="0.05")["status"]=="HELD_SOURCE_VERIFICATION"


def test_synthetic_future_source_reserves_liquidity_winner_and_journals_both_ids(evidence):
    _,future,ids,ledger=evidence
    result=reserve(ledger,future,ids)
    assert result["status"]=="RESERVED" and result["command"]["symbol"]=="STOCK1"
    ranking=result["command"]["selection"]["ranking"]
    assert ranking[0]["setup_receipt_id"]==ids[("STOCK1","09:55")]
    assert ranking[0]["breakout_receipt_id"]==ids[("STOCK1","10:05")]
    assert ledger.read("account")["position"] is None
    assert reserve(ledger,future,ids)["status"]=="ALREADY_RESERVED"


def test_synthetic_future_receipt_to_fill_ema_exit_and_recovery(evidence):
    _,future,ids,ledger=evidence
    reserve(ledger,future,ids)
    def manage(clock):
        return manage_from_receipt(ForwardPaperLedger(ledger.database_url),"account",future,
            ids[("STOCK1",clock)],decision_at=(stamp(clock)+timedelta(seconds=20)).isoformat(),
            participation_pct="1",slippage_bps="0",tick_size="0.05")
    # The bar opened at 10:05, before the 10:05:20 reservation. It cannot fill.
    with pytest.raises(ValueError,match="prospective later bar"):manage("10:10")
    assert manage("10:15")["state"]["position"]
    assert manage("10:20")["state"]["position"]  # EMA request, still exposed
    assert manage("10:25")["state"]["position"] is None
    state=ledger.read("account")
    assert state["used_entry_dates"]==["2026-11-02"]
    assert Decimal(state["cash"])==Decimal("980000")+Decimal(state["realised_pnl"])
    ledger.audit("account")


def test_unverified_reference_universe_stays_held_even_with_future_receipt_fixture(evidence):
    _,future,ids,ledger=evidence
    # A valid content hash is not itself tradability clearance.
    from src import persisted_paper_bridge as module
    old=module.read_universe
    try:
        module.read_universe=lambda *a:{"mode":"LIQUIDITY_RESEARCH_ONLY"}
        assert reserve(ledger,future,ids)["status"]=="HELD_UNIVERSE_REFERENCE"
    finally:module.read_universe=old


@pytest.mark.parametrize("clock",["10:05:09","10:06:31"])
def test_selection_cannot_precede_known_time_or_use_stale_bar(evidence,clock):
    _,future,ids,ledger=evidence
    with pytest.raises(ValueError):
        reserve_from_receipts(ledger,"account",future,pairs(ids),decision_at=at(clock).isoformat(),
                              round_trip_cost_per_share="1")


def test_uploaded_prices_and_flags_are_not_bridge_inputs(evidence):
    _,future,ids,ledger=evidence
    value=pairs(ids);value[0]["timestamp_verified"]=True
    with pytest.raises(ValueError,match="IDs only"):
        reserve_from_receipts(ledger,"account",future,value,decision_at=at("10:05:20").isoformat(),
                              round_trip_cost_per_share="1")


def test_completed_bar_receipt_is_after_interval_but_setup_must_precede_open():
    value=batch();value["candidates"]=value["candidates"][:1]
    c=value["candidates"][0]
    c.update(evidence_kind="COMPLETED_BAR_RECEIPT",breakout_observed_at=value["decision_at"])
    assert EntryBatch.model_validate(value)
    c["setup_known_at"]="2026-11-02T09:45:01+05:30"
    with pytest.raises(ValueError):EntryBatch.model_validate(value)


def test_legacy_tick_batch_fingerprint_is_unchanged():
    value=canonical_batch(EntryBatch.model_validate(batch()))
    # Golden from the deployed pre-bridge implementation at blob 7c662747.
    assert hashlib.sha256(encode(value).encode()).hexdigest()=="fa837041f88a86bfd909c3c621ec844b72d8923c480692979be4fd22e262277f"
    assert all(not any(k in c for k in ("evidence_kind","setup_receipt_id","breakout_receipt_id"))
               for c in value["candidates"])

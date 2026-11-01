"""Synthetic database fixtures test human choice, never market readiness."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from copy import deepcopy
import hashlib
import json
import os
from uuid import uuid4
from urllib.parse import urlencode

import pytest
from src.paper_choice import PaperChoiceStore,ChoiceConflict,ACCOUNT,HumanChoicePaperLedger
from src.universe_store import UniverseStore
from src.universe_scanner import UniverseScanStore, candidate_from,prepare_history,digest
from src.forward_paper_ledger import encode,ForwardPaperLedger,initial_state
from src.daily_universe_refresh import reference_dates_for
from src.run_forward_capture import CALENDAR
from tests.test_universe_scanner import at,bars


def seed(url):
    store=PaperChoiceStore(url);u=UniverseStore(url);u.initialize()
    dates=reference_dates_for("2026-11-02",json.loads(CALENDAR.read_text()))
    report={"mode":"LIQUIDITY_RESEARCH_ONLY","execution_enabled":False,"tradable_count":0,
        "restrictions_verified":False,"calendar_completeness_verified":False,
        "target_date":"2026-11-02","asof_date":dates[-1],"candidates":[
            dict(symbol="STOCK"+str(i),dhan_security_id=str(100+i),reference_price_band="20",
                 reference_review_status="HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE",
                 metrics={"avg_turnover_20d_cr":str((i+1)*100)}) for i in range(2)]}
    payload,proof=encode(report),'{}';revision=hashlib.sha256((payload+'\n'+proof).encode()).hexdigest()
    p="%s" if store.postgres else "?"
    with store.connection() as db:
        db.execute("INSERT INTO universe_research_snapshots VALUES ("+','.join([p]*6)+")",
                   (revision,"2026-11-02",dates[-1],at("08:30:00").isoformat(),payload,proof))
    scan=UniverseScanStore(url);scan.initialize();ids=[]
    history=bars(history=True);raw=bars()
    for data in (history,raw):
        for k,v in (("open",1000),("high",1001),("low",999),("close",1000)):
            data[k]=[v]*len(data[k])
    previous=prepare_history(history,at(),dates)
    for i in range(2):
        sid=str(100+i);symbol="STOCK"+str(i)
        scan.save_reference(revision,sid,history)
        candidate=candidate_from(symbol,previous,raw,at(),at("09:45:00"))
        r=store.record(revision,sid,candidate,digest(history),digest(raw),at().isoformat(),
                       clock=lambda:at("09:45:11"))["receipt"]
        # Synthetic ARMED output isolates UI/choice persistence from detector tests.
        r["scanner_result"].update(status="ARMED",entry="1000",stop="990")
        with store.connection() as db:
            db.execute("UPDATE universe_receipt_signals SET payload="+p+",sha256="+p+" WHERE receipt_id="+p,
                       (encode(r),digest(r),r["receipt_id"]))
        ids.append(r["receipt_id"])
    scan.save_cycle(dict(cycle_id="c"*64,candle_close=at("09:45:00").isoformat(),
        universe_revision=revision,mode="FULL_UNIVERSE_RESEARCH_ONLY",execution_enabled=False,
        forward_paper_ready=False,rows=[dict(symbol="STOCK"+str(i),security_id=str(100+i),
            selected=True,status="SCANNED",setup_status="ARMED",receipt_id=ids[i]) for i in range(2)]))
    return store,ids


@pytest.fixture(params=["sqlite","postgres"])
def inputs(tmp_path,request):
    url="sqlite:///"+str(tmp_path/"choice.db");cleanup=None
    if request.param=="postgres":
        if not os.getenv("TEST_UNIVERSE_DATABASE_URL"):pytest.skip("PostgreSQL CI only")
        import psycopg
        from psycopg import sql
        base=os.environ["TEST_UNIVERSE_DATABASE_URL"];schema="choice_"+uuid4().hex
        with psycopg.connect(base) as db:db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        url=base+("&" if '?' in base else '?')+urlencode({"options":"-csearch_path="+schema})
        def cleanup():
            with psycopg.connect(base) as db:db.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    try:yield seed(url)
    finally:
        if cleanup:cleanup()


def command(rid,request="first",expected=None):
    return dict(action="CHOOSE",receipt_id=rid,request_id=request,expected_choice_id=expected)


def test_user_can_choose_lower_ranked_stock_without_any_order(inputs):
    store,ids=inputs
    workspace=store.workspace(at("09:45:20"))
    assert [c["symbol"] for c in workspace["candidates"]]==["STOCK1","STOCK0"]
    result=store.choose(command(ids[0]),at("09:45:20"))
    assert result["selected"]["symbol"]=="STOCK0" and result["status"]=="SELECTED_HELD"
    assert not result["execution_enabled"] and not result["paper_runtime_enabled"]
    assert not result["selected"]["selection_is_order"]
    assert store.workspace(at("09:45:21"))["position"] is None
    with store.connection() as db:assert not store.table_exists(db,"forward_paper_accounts")


def test_idempotent_retry_and_restart_preserve_original_user_decision(inputs):
    store,ids=inputs;first=store.choose(command(ids[0]),at("09:45:20"))
    retry=PaperChoiceStore(store.database_url).choose(command(ids[0]),at("10:00:00"))
    assert retry["duplicate"] and retry["selected"]==first["selected"]
    with pytest.raises(ChoiceConflict):store.choose(command(ids[1]),at("09:45:21"))


def test_stale_tabs_cannot_replace_or_withdraw_another_selection(inputs):
    store,ids=inputs;first=store.choose(command(ids[0]),at("09:45:20"))
    with pytest.raises(ChoiceConflict):store.choose(command(ids[1],"other"),at("09:45:21"))
    result=store.choose(command(ids[1],"replace",first["selected"]["choice_id"]),at("09:45:22"))
    assert result["selected"]["symbol"]=="STOCK1"
    cancel=dict(action="WITHDRAW",receipt_id=None,request_id="cancel",expected_choice_id=result["selected"]["choice_id"])
    assert store.choose(cancel,at("09:45:23"))["status"]=="WITHDRAWN"
    workspace=store.workspace(at("09:45:24"))
    assert workspace["selected"] is None and len(workspace["choice_journal"])==3


@pytest.mark.parametrize("clock",["09:47:00","11:30:00"])
def test_stale_or_closed_window_choice_cannot_be_saved(inputs,clock):
    store,ids=inputs
    with pytest.raises(ChoiceConflict):store.choose(command(ids[0]),at(clock))


def test_unknown_or_wrong_instrument_receipt_cannot_be_selected(inputs):
    store,_=inputs
    with pytest.raises(ChoiceConflict):store.choose(command("a"*64),at("09:45:20"))


def test_concurrent_manual_choices_reserve_only_one_current_stock(inputs):
    store,ids=inputs;store.initialize_choices()
    def choose(i):
        try:return store.choose(command(ids[i%2],"worker"+str(i)),at("09:45:20"))["status"]
        except ChoiceConflict:return "CONFLICT"
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(choose,range(4)))
    assert results.count("SELECTED_HELD")==1


@pytest.mark.parametrize("condition",["open","pending","filled_today"])
def test_trade_in_progress_or_daily_fill_blocks_choice_changes(inputs,condition):
    store,ids=inputs;ledger=ForwardPaperLedger(store.database_url);ledger.initialize()
    state=initial_state()
    if condition=="open":state["position"]={"quantity":1}
    elif condition=="pending":state["orders"]={"order":{"status":"PENDING"}}
    else:state["used_entry_dates"]=["2026-11-02"]
    p="%s" if store.postgres else "?"
    with store.connection() as db:db.execute("INSERT INTO forward_paper_accounts VALUES ("+p+","+p+")",(ACCOUNT,encode(state)))
    with pytest.raises(ChoiceConflict):store.choose(command(ids[0]),at("09:45:20"))


def test_choice_expires_without_becoming_an_order(inputs):
    store,ids=inputs;store.choose(command(ids[0]),at("09:45:20"))
    result=store.workspace(at("11:30:00"))
    assert result["selected"]["effective_status"]=="EXPIRED"
    assert not result["fills"] and not result["position"]


def entry_command(choice):
    return dict(kind="ENTRY_REQUEST",at=at("09:50:20").isoformat(),known_at=at("09:50:20").isoformat(),
        order_id="manual_entry",signal_id="signal",source_sha256="a"*64,
        universe_revision=choice["universe_revision"],symbol=choice["symbol"],security_id=choice["security_id"],
        quantity=10,limit=choice["entry"],stop=choice["initial_stop"],fee_budget="10",
        selection=dict(human_choice_id=choice["choice_id"],setup_receipt_id=choice["receipt_id"]))


def test_atomic_handoff_accepts_only_the_selected_stock_and_then_blocks_replacement(inputs):
    store,ids=inputs
    choice=store.choose(command(ids[0]),at("09:45:20"))["selected"]
    ledger=HumanChoicePaperLedger(store.database_url)
    request=entry_command(choice)
    assert ledger.apply(ACCOUNT,"entry",request)["state"]["orders"]["manual_entry"]["symbol"]=="STOCK0"
    with pytest.raises(ChoiceConflict):
        store.choose(command(ids[1],"replace",choice["choice_id"]),at("09:45:25"))
    assert ledger.audit(ACCOUNT)["event_count"]==1


@pytest.mark.parametrize("change",[dict(symbol="STOCK1",security_id="101"),
    dict(stop="980"),dict(limit="1001"),dict(at="2026-11-02T09:45:19+05:30"),
    dict(selection={}),dict(quantity=10000)])
def test_handoff_cannot_change_human_choice_or_backdate_entry(inputs,change):
    store,ids=inputs;choice=store.choose(command(ids[0]),at("09:45:20"))["selected"]
    request=entry_command(choice);request.update(change)
    with pytest.raises(ValueError):HumanChoicePaperLedger(store.database_url).apply(ACCOUNT,"entry",request)


def test_replaced_choice_is_checked_under_same_account_lock_as_entry(inputs):
    store,ids=inputs;first=store.choose(command(ids[0]),at("09:45:20"))["selected"]
    store.choose(command(ids[1],"replace",first["choice_id"]),at("09:45:21"))
    with pytest.raises(ChoiceConflict):
        HumanChoicePaperLedger(store.database_url).apply(ACCOUNT,"stale_entry",entry_command(first))


def test_changed_stored_choice_is_rejected_before_handoff(inputs):
    store,ids=inputs;choice=store.choose(command(ids[0]),at("09:45:20"))["selected"]
    changed=deepcopy(choice);changed["initial_stop"]="980"
    p="%s" if store.postgres else "?"
    with store.connection() as db:
        db.execute("UPDATE paper_stock_choices SET payload="+p,(encode(changed),))
    with pytest.raises(ValueError,match="integrity"):
        HumanChoicePaperLedger(store.database_url).apply(ACCOUNT,"changed_choice",entry_command(choice))


def test_no_stock_choice_means_no_entry_even_for_valid_sizing(inputs):
    store,ids=inputs
    hypothetical=store.catalog(at("09:45:20"))[0][0]
    hypothetical["choice_id"]="a"*64
    with pytest.raises(ChoiceConflict):
        HumanChoicePaperLedger(store.database_url).apply(ACCOUNT,"no_choice",entry_command(hypothetical))

"""Inactive chosen-stock paper controller. No broker order calls or scheduler.

The default source can only read current research receipts, whose clearance
flags remain false. A future verified-source producer is still required.
"""
from datetime import timedelta,time
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
import hashlib
import json

from src.forward_paper_ledger import encode,instant,amount
from src.paper_choice import PaperChoiceStore,HumanChoicePaperLedger,ACCOUNT,COST
from src.risk_engine import RiskPolicy,size_long
from src.paper_trade_management import simulate_paper_bar
from src.paper_trade_journal import trade_journal

FLAGS=("timestamp_verified","session_contract_verified","reference_prices_verified",
       "breakout_receipts_verified")


class CommittedPaperSource(PaperChoiceStore):
    def latest_for(self,symbol,security_id,revision,day):
        p="%s" if self.postgres else "?"
        def field(name):return "(payload::jsonb ->> '"+name+"')" if self.postgres else "json_extract(payload,'$."+name+"')"
        with self.connection() as db:
            if not self.table_exists(db,"universe_receipt_signals"):return None
            query=("SELECT receipt_id FROM universe_receipt_signals WHERE "+field("symbol")+"="+p+
                " AND "+field("security_id")+"="+p+" AND "+field("universe_revision")+"="+p+
                " AND "+field("candle_close")+" LIKE "+p+" ORDER BY "+field("candle_close")+" DESC LIMIT 1")
            row=db.execute(query,(symbol,security_id,revision,day+"T%")).fetchone()
        return self.read(row[0]) if row else None

    def reference_cleared(self,receipt):
        # The current producer never writes this mode/clearance. This method
        # deliberately does not promote research holds into paper eligibility.
        p="%s" if self.postgres else "?"
        with self.connection() as db:
            row=db.execute("SELECT payload,evidence FROM universe_research_snapshots WHERE revision="+p,
                           (receipt["universe_revision"],)).fetchone()
        if not row or hashlib.sha256((row[0]+"\n"+row[1]).encode()).hexdigest()!=receipt["universe_revision"]:
            raise ValueError("Immutable paper reference required")
        report=json.loads(row[0])
        return (report.get("mode")=="VERIFIED_PAPER_UNIVERSE" and report.get("restrictions_verified") is True
                and report.get("calendar_completeness_verified") is True
                and report["target_date"]==instant(receipt["candle_close"]).date().isoformat())


class HumanPaperController:
    def __init__(self,source):
        self.source=source;self.ledger=HumanChoicePaperLedger(source.database_url)

    def result(self,status,**extra):
        return dict(status=status,execution_enabled=False,paper_runtime_enabled=False,**extra)

    def clock(self,now):
        slot=now.replace(minute=now.minute//5*5,second=0,microsecond=0)
        eid="clock_"+hashlib.sha256(slot.isoformat().encode()).hexdigest()
        old=self.ledger.event(ACCOUNT,eid)
        command=old["command"] if old else dict(kind="PAPER_CLOCK",at=now.isoformat())
        try:self.ledger.apply(ACCOUNT,eid,command)
        except ValueError:
            # Competing worker clocks may differ by milliseconds; only a
            # committed existing command is reused. No fresh fill is backdated.
            if not self.ledger.event(ACCOUNT,eid):raise

    def run_once(self,now):
        now=instant(now.isoformat())
        with self.source.connection() as db:
            account=self.source.account(db);choice=self.source.selected(db)
        exposure=bool(account and (account["position"] or any(o["status"]=="PENDING" for o in account["orders"].values())))
        if exposure:
            # Always request/cancel/mark deadline state BEFORE consulting feed.
            self.clock(now)
            with self.source.connection() as db:account=self.source.account(db)
        from src.run_forward_capture import CALENDAR
        calendar=json.loads(CALENDAR.read_text());day=now.date().isoformat()
        if day not in calendar["sessions"] or not calendar["earliest_target"]<=day<=calendar["latest_target"]:
            return self.result("HELD_UNREVIEWED_SESSION",outstanding_exposure=bool(account and account["position"]))
        if account and not account["position"] and day in account["used_entry_dates"]:
            return self.result("DAILY_ENTRY_USED",journal=trade_journal(account))
        pending=[o for o in (account["orders"].values() if account else []) if o["status"]=="PENDING"]
        bound=account["orders"][account["position"]["entry_order_id"]] if account and account["position"] else next(iter(pending),None)
        if not bound:
            if not choice:return self.result("NO_STOCK_CHOICE")
            if instant(choice["chosen_at"]).date()!=now.date() or now.time()>=time(11,30):
                return self.result("CHOICE_EXPIRED")
            if now.time()<time(9,45):return self.result("OUTSIDE_ENTRY_WINDOW")
            if account and any(o.get("selection",{}).get("human_choice_id")==choice["choice_id"] for o in account["orders"].values()):
                return self.result("CHOICE_ALREADY_ATTEMPTED")
            identity=choice
        else:identity=bound
        receipt=self.source.latest_for(identity["symbol"],identity["security_id"],identity["universe_revision"],day)
        if not receipt:return self.result("HELD_MISSING_RECEIPT",outstanding_exposure=bool(account and account["position"]))
        close=instant(receipt["candle_close"]);known=instant(receipt["known_at"])
        if any(receipt.get(k)!=identity[k] for k in ("symbol","security_id","universe_revision")) or close.date()!=now.date():
            raise ValueError("Management receipt instrument/session mismatch")
        if not timedelta()<=now-close<=timedelta(seconds=90) or known>now:
            return self.result("HELD_STALE_OR_FUTURE_RECEIPT",outstanding_exposure=bool(account and account["position"]))
        if any(receipt.get(flag) is not True for flag in FLAGS) or not self.source.reference_cleared(receipt):
            return self.result("HELD_SOURCE_VERIFICATION",outstanding_exposure=bool(account and account["position"]))
        if bound:
            if bound["side"]=="BUY" and close-timedelta(minutes=5)<=instant(bound["known_at"]):
                return self.result("WAIT_FOR_FULL_POST_DECISION_BAR")
            return self.manage(receipt,now)
        setup=self.source.read(choice["receipt_id"])
        if (not setup or any(setup.get(f) is not True for f in FLAGS) or
                setup.get("receipt_status")!="TIMELY_RESEARCH_EVIDENCE"):
            return self.result("HELD_CHOSEN_SETUP_VERIFICATION")
        if (setup["symbol"]!=choice["symbol"] or setup["security_id"]!=choice["security_id"] or
                setup["universe_revision"]!=receipt["universe_revision"] or
                setup["reference_sha256"]!=receipt["reference_sha256"] or
                instant(setup["known_at"])>instant(choice["chosen_at"]) or
                Decimal(setup["scanner_result"]["entry"])!=Decimal(choice["entry"]) or
                Decimal(setup["scanner_result"]["stop"])!=Decimal(choice["initial_stop"]) or
                setup["scanner_result"]["status"]!="ARMED"):
            raise ValueError("Chosen setup identity changed")
        if close<=instant(choice["candle_close"]):return self.result("WAIT_FOR_LATER_BREAKOUT")
        entry,stop=Decimal(choice["entry"]),Decimal(choice["initial_stop"])
        tail=[b for b in receipt["candles"] if instant(b["time"])>instant(choice["candle_close"])]
        if any(Decimal(b["low"])<=stop for b in tail):return self.result("CHOICE_INVALIDATED_STOP")
        hits=[b for b in tail if Decimal(b["high"])>=entry]
        if not hits:return self.result("WAIT_FOR_LATER_BREAKOUT")
        first=hits[0]
        if instant(first["time"])-timedelta(minutes=5)<=instant(choice["chosen_at"]):
            return self.result("HELD_BREAKOUT_BEFORE_FULL_CHOICE_BAR")
        if instant(first["time"])!=close:return self.result("HELD_MISSED_BREAKOUT")
        if now.time()>=time(11,30):return self.result("CHOICE_EXPIRED")
        cash=min(Decimal("980000"),Decimal(account["cash"])) if account else Decimal("980000")
        execution_cost=(COST+stop*Decimal("0.0005")+Decimal("0.05")).quantize(Decimal("0.000001"),rounding=ROUND_CEILING)
        sized=size_long(entry,stop,execution_cost,policy=RiskPolicy(capital=cash))
        qty=min(sized.quantity,choice["quantity"],int((cash/(entry+execution_cost)).to_integral_value(rounding=ROUND_FLOOR)))
        if qty<=0:return self.result("HELD_RISK_OR_CAPITAL")
        oid="choice_entry_"+hashlib.sha256(encode([choice["choice_id"],receipt["receipt_id"]]).encode()).hexdigest()
        command=dict(kind="ENTRY_REQUEST",at=now.isoformat(),known_at=now.isoformat(),order_id=oid,
            signal_id=hashlib.sha256(encode([choice["receipt_id"],receipt["receipt_id"]]).encode()).hexdigest(),
            source_sha256=receipt["current_sha256"],universe_revision=choice["universe_revision"],
            symbol=choice["symbol"],security_id=choice["security_id"],quantity=qty,limit=amount(entry),stop=amount(stop),
            fee_budget=amount(qty*execution_cost),selection=dict(human_choice_id=choice["choice_id"],
                setup_receipt_id=choice["receipt_id"],breakout_receipt_id=receipt["receipt_id"],
                decision="HUMAN_STOCK_CHOICE",round_trip_cost_per_share=amount(COST),
                estimated_execution_cost_per_share=amount(execution_cost),cost_breakeven_includes_execution=True,
                execution_assumptions=dict(version="PAPER_SIM_CLOSE_V1",fill_model="NEXT_TIMELY_CLOSE_AT_RECEIPT",
                    participation_pct="1",slippage_bps="5",tick_size="0.05"),
                source_attestations={f:True for f in FLAGS}))
        old=self.ledger.event(ACCOUNT,oid) if account else None
        if old:command["at"]=command["known_at"]=old["command"]["at"]
        try:result=self.ledger.apply(ACCOUNT,oid,command)
        except ValueError:
            if not self.ledger.event(ACCOUNT,oid):raise
            result={"status":"ALREADY_APPLIED"}
        return self.result("ENTRY_RESERVED",ledger_status=result["status"],choice_id=choice["choice_id"])

    def manage(self,receipt,now):
        from src.universe_scanner import prepare_history,candidate_from,digest
        from src.universe_receipts import canonical_candidate
        from src.daily_universe_refresh import reference_dates_for
        from src.run_forward_capture import CALENDAR
        from src.candle_pipeline import ema
        p="%s" if self.source.postgres else "?"
        with self.source.connection() as db:
            account=self.source.account(db)
            entry=account["orders"][account["position"]["entry_order_id"]] if account["position"] else next(
                o for o in account["orders"].values() if o["side"]=="BUY" and o["status"]=="PENDING")
            row=db.execute("SELECT payload FROM universe_scan_reference_cache WHERE revision="+p+" AND security_id="+p,
                           (receipt["universe_revision"],receipt["security_id"])).fetchone()
        if not row or digest(json.loads(row[0]))!=receipt["reference_sha256"]:raise ValueError("Management reference mismatch")
        calendar=json.loads(CALENDAR.read_text());close=instant(receipt["candle_close"])
        previous=prepare_history(json.loads(row[0]),now,reference_dates_for(close.date().isoformat(),calendar))
        current=receipt["candles"]
        raw={"timestamp":[int(instant(b["time"]).timestamp())-300 for b in current],
             **{k:[b[k] for b in current] for k in ("open","high","low","close","volume")}}
        candidate=candidate_from(receipt["symbol"],previous,raw,now,close)
        if digest(canonical_candidate(candidate))!=receipt["candidate_sha256"]:raise ValueError("Management input mismatch")
        last=current[-1]
        assumptions=entry["selection"].get("execution_assumptions")
        if not assumptions or assumptions.get("version")!="PAPER_SIM_CLOSE_V1":
            return self.result("HELD_PINNED_EXECUTION_ASSUMPTIONS",outstanding_exposure=bool(account["position"]))
        value=dict(kind="SIMULATED_BAR",at=now.isoformat(),close_at=close.isoformat(),symbol=receipt["symbol"],
            security_id=receipt["security_id"],universe_revision=receipt["universe_revision"],
            source_sha256=receipt["current_sha256"],close=last["close"],high=last["high"],low=last["low"],
            volume=last["volume"],ema10=str(ema([*candidate.ema_warmup_closes,*[b.close for b in candidate.completed_5m]],10)),
            **{k:assumptions[k] for k in ("participation_pct","slippage_bps","tick_size")},**{f:True for f in FLAGS})
        eid="bar_"+hashlib.sha256(encode([receipt["symbol"],receipt["security_id"],close.isoformat()]).encode()).hexdigest()
        old=self.ledger.event(ACCOUNT,eid)
        if old:value["at"]=old["command"]["at"]
        result=simulate_paper_bar(self.ledger,ACCOUNT,value)
        return self.result("PAPER_BAR_PROCESSED",ledger_status=result["status"],journal=trade_journal(result["state"]))


def collect_chosen_receipt(source,identity,now,token,*,clock,fetch=None):
    """Read-only, one-instrument feed for the chosen stock or existing exposure.

    It retains the recorder's false verification flags. It does not certify the
    OPEN timestamp/session assumptions used to normalize these research prices.
    """
    from src.dhan_history_client import fetch_intraday
    from src.universe_scanner import prepare_history,candidate_from,digest
    from src.daily_universe_refresh import reference_dates_for
    from src.run_forward_capture import CALENDAR
    import httpx
    if not token:return {"status":"HELD_FEED_TOKEN_UNAVAILABLE"}
    p="%s" if source.postgres else "?"
    with source.connection() as db:
        row=db.execute("SELECT payload,sha256 FROM universe_scan_reference_cache WHERE revision="+p+" AND security_id="+p,
                       (identity["universe_revision"],identity["security_id"])).fetchone()
    if not row or digest(json.loads(row[0]))!=row[1]:return {"status":"HELD_REFERENCE_CACHE"}
    try:
        raw=(fetch or fetch_intraday)(token,identity["security_id"],5,
            (now-timedelta(days=1)).strftime("%Y-%m-%d 09:15:00"),
            (now+timedelta(days=1)).strftime("%Y-%m-%d 09:15:00"))
        observed=instant(clock().isoformat())
        close=now.replace(minute=now.minute//5*5,second=0,microsecond=0)
        calendar=json.loads(CALENDAR.read_text())
        previous=prepare_history(json.loads(row[0]),observed,reference_dates_for(now.date().isoformat(),calendar))
        candidate=candidate_from(identity["symbol"],previous,raw,observed,close)
        result=source.record(identity["universe_revision"],identity["security_id"],candidate,
            row[1],digest(raw),observed.isoformat(),clock=clock)
        return {"status":result["status"],"receipt_id":result["receipt"]["receipt_id"]}
    except (httpx.HTTPError,ValueError,TypeError,KeyError,OverflowError) as exc:
        return {"status":"HELD_FEED_FAILURE","error_type":type(exc).__name__}


def save_worker_status(source,result,now):
    """Operational heartbeat only; never replaces immutable trade evidence."""
    p="%s" if source.postgres else "?"
    payload=dict(at=now.isoformat(),enabled=True,status=result["status"],
                 feed_status=result.get("feed_status"),execution_enabled=False)
    with source.connection() as db:
        if source.postgres:db.execute("SELECT pg_advisory_xact_lock(73031011)")
        else:db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS paper_worker_status (account_id TEXT PRIMARY KEY,payload TEXT NOT NULL)")
        old=db.execute("SELECT payload FROM paper_worker_status WHERE account_id="+p,(ACCOUNT,)).fetchone()
        if old and instant(json.loads(old[0])["at"])>now:return
        db.execute("INSERT INTO paper_worker_status VALUES ("+p+","+p+") "
                   "ON CONFLICT(account_id) DO UPDATE SET payload=excluded.payload",(ACCOUNT,encode(payload)))


def run_configured_cycle(*,clock=None,fetch=None):
    """Future worker entrypoint. Not imported by the deployed scheduler/API.

    The switch alone cannot clear actual research source verification holds.
    """
    import os
    from datetime import datetime
    from src.forward_paper_ledger import IST
    if os.getenv("FORWARD_PAPER_ENABLED")!="true":
        return {"status":"PAPER_CONTROLLER_DISABLED","execution_enabled":False,"paper_runtime_enabled":False}
    url=os.getenv("SCAN_DATABASE_URL","")
    if not url.startswith(("postgresql://","postgres://")):
        return {"status":"PAPER_STORE_REQUIRED","execution_enabled":False,"paper_runtime_enabled":False}
    clock=clock or (lambda:datetime.now(IST));now=instant(clock().isoformat())
    try:
        source=CommittedPaperSource(url);controller=HumanPaperController(source)
        with source.connection() as db:
            account=source.account(db);choice=source.selected(db)
        pending=[o for o in (account["orders"].values() if account else []) if o["status"]=="PENDING"]
        if account and (account["position"] or pending):
            controller.clock(now)
            with source.connection() as db:account=source.account(db)
            pending=[o for o in account["orders"].values() if o["status"]=="PENDING"]
        identity=account["orders"][account["position"]["entry_order_id"]] if account and account["position"] else next(iter(pending),choice)
        from src.run_forward_capture import CALENDAR
        calendar=json.loads(CALENDAR.read_text());day=now.date().isoformat()
        feed={"status":"NO_FEED_REQUEST"}
        used=bool(account and day in account["used_entry_dates"] and not account["position"] and not pending)
        if (identity and not used and day in calendar["sessions"] and calendar["earliest_target"]<=day<=calendar["latest_target"]
                and time(9,45)<=now.time()<=time(15,15)
                and (pending or account and account["position"] or instant(identity["chosen_at"]).date()==now.date() and now.time()<time(11,30))):
            feed=collect_chosen_receipt(source,identity,now,os.getenv("DHAN_ACCESS_TOKEN"),clock=clock,fetch=fetch)
        result=controller.run_once(clock())
        result={**result,"feed_status":feed["status"],"paper_runtime_enabled":True}
        save_worker_status(source,result,instant(clock().isoformat()))
        return result
    except Exception as exc:
        return {"status":"PAPER_CONTROLLER_FAILED","error_type":type(exc).__name__,
                "exposure_status":"UNKNOWN","execution_enabled":False,"paper_runtime_enabled":False}

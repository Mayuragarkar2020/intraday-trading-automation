"""Human stock choice and its durable journal; never an order executor."""
import hashlib
import json
from datetime import datetime, timedelta, time
from decimal import Decimal, ROUND_FLOOR

from src.forward_paper_ledger import encode, instant, identifier, amount, ForwardPaperLedger
from src.risk_engine import RiskPolicy, size_long
from src.universe_receipts import UniverseReceiptStore
from src.universe_store import UniverseStore
from src.paper_trade_journal import trade_journal

ACCOUNT="paper-main"  # pinned: API clients cannot reset daily limits/account IDs
COST=Decimal("1")     # explicit paper assumption, not certified broker charges


class ChoiceConflict(ValueError): pass


class PaperChoiceStore(UniverseReceiptStore):
    def table_exists(self,db,name):
        if self.postgres:
            return db.execute("SELECT to_regclass(%s)",(name,)).fetchone()[0] is not None
        return db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",(name,)).fetchone() is not None

    def initialize_choices(self):
        with self.connection() as db:
            if self.postgres: db.execute("SELECT pg_advisory_xact_lock(73031030)")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_stock_choices (
                choice_id TEXT PRIMARY KEY, payload TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_choice_current (
                account_id TEXT PRIMARY KEY, choice_id TEXT)""")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_choice_events (
                account_id TEXT NOT NULL, request_id TEXT NOT NULL,
                command TEXT NOT NULL, result TEXT NOT NULL, at TEXT NOT NULL,
                PRIMARY KEY(account_id,request_id))""")

    def account(self,db):
        if not self.table_exists(db,"forward_paper_accounts"): return None
        p="%s" if self.postgres else "?"
        row=db.execute("SELECT payload FROM forward_paper_accounts WHERE account_id="+p,(ACCOUNT,)).fetchone()
        return json.loads(row[0]) if row else None

    def selected(self,db):
        if not self.table_exists(db,"paper_choice_current"):return None
        p="%s" if self.postgres else "?"
        row=db.execute("SELECT c.choice_id,c.payload FROM paper_choice_current a JOIN paper_stock_choices c "
                       "ON a.choice_id=c.choice_id WHERE a.account_id="+p,(ACCOUNT,)).fetchone()
        if not row:return None
        choice=json.loads(row[1]);identity=choice.pop("choice_id")
        if identity!=row[0] or hashlib.sha256(encode(choice).encode()).hexdigest()!=identity:
            raise ValueError("Stock choice integrity failure")
        return {**choice,"choice_id":identity}

    def catalog(self,now):
        now=instant(now.isoformat())
        if now.weekday()>=5 or not time(9,45)<=now.time()<time(11,30):
            return [],"OUTSIDE_ENTRY_WINDOW"
        with self.connection() as db:
            if not self.table_exists(db,"universe_scan_cycles"):return [],"WAITING_FOR_SCAN"
            row=db.execute("SELECT payload FROM universe_scan_cycles WHERE mode='FULL_UNIVERSE_RESEARCH_ONLY' "
                           "ORDER BY candle_close DESC,cycle_id DESC LIMIT 1").fetchone()
            account=self.account(db)
        if not row:return [],"WAITING_FOR_SCAN"
        cycle=json.loads(row[0]);close=instant(cycle["candle_close"])
        if cycle.get("execution_enabled") is not False or cycle.get("forward_paper_ready") is not False:
            raise ValueError("Unexpected scanner mode")
        if close.date()!=now.date() or not timedelta()<=now-close<=timedelta(seconds=90):
            return [],"WAITING_FOR_FRESH_SCAN"
        published=UniverseStore(self.database_url).latest(now.date().isoformat())
        if (not published or published["revision"]!=cycle["universe_revision"] or
                instant(published["created_at"]).date()!=now.date() or instant(published["created_at"])>now):
            return [],"WAITING_FOR_SAME_DAY_UNIVERSE"
        candidates=[]
        cash=min(Decimal("980000"),Decimal(account["cash"])) if account else Decimal("980000")
        if cash<=0:return [],"INSUFFICIENT_CAPITAL"
        for row in cycle["rows"]:
            if not (row.get("selected") and row.get("status")=="SCANNED" and
                    row.get("setup_status")=="ARMED" and row.get("receipt_id")):continue
            receipt=self.read(row["receipt_id"])
            if (not receipt or receipt["symbol"]!=row["symbol"] or
                    receipt["security_id"]!=row["security_id"] or receipt["candle_close"]!=cycle["candle_close"]
                    or receipt["universe_revision"]!=published["revision"] or
                    instant(receipt["known_at"])>now or receipt["scanner_result"]["status"]!="ARMED"):
                raise ValueError("Choice source binding mismatch")
            refs=[r for r in published["snapshot"]["candidates"] if r.get("symbol")==row["symbol"]]
            if len(refs)!=1:raise ValueError("Unique choice instrument required")
            ref=refs[0]
            if (str(ref.get("dhan_security_id"))!=row["security_id"] or
                    ref.get("reference_price_band") not in (10,20,"10","20","No Band") or
                    ref.get("reference_review_status") not in ("HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE","VERIFIED")):
                continue
            entry,stop=(Decimal(receipt["scanner_result"][k]) for k in ("entry","stop"))
            if not Decimal("300")<=entry<=Decimal("5000"):continue
            sizing=size_long(entry,stop,COST,policy=RiskPolicy(capital=cash))
            qty=min(sizing.quantity,int((cash/(entry+COST)).to_integral_value(rounding=ROUND_FLOOR)))
            candidates.append(dict(receipt_id=receipt["receipt_id"],symbol=row["symbol"],security_id=row["security_id"],
                universe_revision=published["revision"],candle_close=cycle["candle_close"],
                entry=amount(entry),initial_stop=amount(stop),quantity=qty,
                estimated_cost_per_share=amount(COST),planned_risk=amount((entry-stop+COST)*qty),
                gross_exposure=amount(entry*qty),avg_turnover_20d_cr=ref["metrics"]["avg_turnover_20d_cr"],
                readiness="HELD_DATA_VERIFICATION",selection_is_order=False))
        candidates.sort(key=lambda c:(-Decimal(c["avg_turnover_20d_cr"]),c["symbol"]))
        return candidates,"SHORTLIST_AVAILABLE" if candidates else "NO_SETUP_READY_STOCKS"

    def workspace(self,now):
        now=instant(now.isoformat())
        candidates,status=self.catalog(now)
        with self.connection() as db:
            selected=self.selected(db);account=self.account(db)
            worker=None
            if self.table_exists(db,"paper_worker_status"):
                p="%s" if self.postgres else "?"
                row=db.execute("SELECT payload FROM paper_worker_status WHERE account_id="+p,(ACCOUNT,)).fetchone()
                worker=json.loads(row[0]) if row else None
            events=[]
            if self.table_exists(db,"paper_choice_events"):
                p="%s" if self.postgres else "?"
                events=[json.loads(r[0]) for r in db.execute("SELECT result FROM paper_choice_events "
                    "WHERE account_id="+p+" ORDER BY at DESC,request_id DESC LIMIT 20",(ACCOUNT,)).fetchall()]
        if selected:
            selected={**selected,"effective_status":"SELECTED_HELD" if
                instant(selected["chosen_at"]).date()==now.date() and now.time()<time(11,30) else "EXPIRED"}
        pending=[o for o in (account["orders"].values() if account else []) if o["status"]=="PENDING"]
        phase=("EXIT_PENDING" if any(o["side"]=="SELL" for o in pending) else "MANAGING") if account and account["position"] else (
            "WAITING_ENTRY_FILL" if pending else "COMPLETED" if account and now.date().isoformat() in account["used_entry_dates"] else
            selected["effective_status"] if selected else "NO_STOCK_CHOICE")
        if selected and account and phase=="SELECTED_HELD" and any(o.get("selection",{}).get("human_choice_id")==selected["choice_id"]
                and o["status"]=="IOC_CANCELLED" and not o["filled"] for o in account["orders"].values()):phase="ENTRY_CANCELLED"
        if selected and phase in {"EXIT_PENDING","MANAGING","WAITING_ENTRY_FILL","COMPLETED","ENTRY_CANCELLED"}:
            selected["effective_status"]=phase
        occupied=bool(account and (account["position"] or any(o["status"]=="PENDING" for o in account["orders"].values())
                                   or now.date().isoformat() in account["used_entry_dates"]))
        return dict(mode="HUMAN_CHOICE_PAPER_PREVIEW",execution_enabled=False,paper_runtime_enabled=bool(worker and worker.get("enabled")),
            paper_worker=worker,paper_worker_fresh=bool(worker and timedelta()<=now-instant(worker["at"])<=timedelta(minutes=7)),
            status=status,management_state=phase,candidates=candidates,selected=selected,selection_blocked=occupied,
            position=account["position"] if account else None,
            fills=(account["fills"][-20:] if account else []),
            realised_pnl=account["realised_pnl"] if account else "0",choice_journal=events,
            **trade_journal(account),
            last_price_at=(account.get("management",{}).get("last_close_at") if account else None),
            last_control_at=account["last_at"] if account else None,
            price_feed_stale=bool(account and account["position"] and (not account.get("management",{}).get("last_close_at") or
                now-instant(account["management"]["last_close_at"])>timedelta(minutes=7))),
            closure_deadline_breached=bool(account and account.get("management",{}).get("closure_deadline_breached")),
            policy=dict(capital="980000",risk_cap="9800",one_filled_entry_per_day=True,
                        close_by="15:00 IST",cost_assumption_per_share=amount(COST)),
            message=("Paper worker status: "+worker["status"]+". Live broker execution is disabled." if worker else
                     "You choose the stock. Paper execution is held until market-data checks and the trading runtime are ready."))

    def choose(self,command,now):
        now=instant(now.isoformat())
        if (set(command)!={"action","request_id","receipt_id","expected_choice_id"} or
                command["action"] not in {"CHOOSE","WITHDRAW"}):
            raise ValueError("Invalid choice command")
        identifier(command["request_id"])
        self.initialize_choices()
        p="%s" if self.postgres else "?"
        with self.connection() as db:
            if self.postgres:db.execute("SELECT pg_advisory_xact_lock(73031011)")
            else:db.execute("BEGIN IMMEDIATE")
            old=db.execute("SELECT command,result FROM paper_choice_events WHERE account_id="+p+
                " AND request_id="+p,(ACCOUNT,command["request_id"])).fetchone()
            if old:
                if old[0]!=encode(command):raise ChoiceConflict("Choice request identity conflict")
                return {**json.loads(old[1]),"duplicate":True}
            current=self.selected(db)
            if command["expected_choice_id"]!=(current["choice_id"] if current else None):
                raise ChoiceConflict("Selection changed. Refresh before choosing again.")
            account=self.account(db)
            if account and (account["position"] or any(o["status"]=="PENDING" for o in account["orders"].values())
                            or now.date().isoformat() in account["used_entry_dates"]):
                raise ChoiceConflict("A trade is pending, open or already filled today.")
            selected=None
            if command["action"]=="CHOOSE":
                candidates,_=self.catalog(now)
                candidate=next((c for c in candidates if c["receipt_id"]==command["receipt_id"]),None)
                if not candidate or not candidate["quantity"]:
                    raise ChoiceConflict("This setup is no longer selectable. Refresh the shortlist.")
                selected={**candidate,"chosen_at":now.isoformat(),"request_id":command["request_id"],
                    "state":"SELECTED_HELD","account_id":ACCOUNT,"selection_is_order":False}
                cid=hashlib.sha256(encode(selected).encode()).hexdigest()
                selected["choice_id"]=cid
                db.execute("INSERT INTO paper_stock_choices VALUES ("+p+","+p+")",(cid,encode(selected)))
            elif not current:raise ChoiceConflict("No stock is selected.")
            db.execute("INSERT INTO paper_choice_current VALUES ("+p+","+p+") "
                "ON CONFLICT(account_id) DO UPDATE SET choice_id=excluded.choice_id",
                (ACCOUNT,selected["choice_id"] if selected else None))
            result=dict(status="SELECTED_HELD" if selected else "WITHDRAWN",selected=selected,
                at=now.isoformat(),action=command["action"],previous_choice_id=current["choice_id"] if current else None,
                execution_enabled=False,paper_runtime_enabled=False,duplicate=False)
            db.execute("INSERT INTO paper_choice_events VALUES ("+",".join([p]*5)+")",
                       (ACCOUNT,command["request_id"],encode(command),encode(result),now.isoformat()))
            return result


class HumanChoicePaperLedger(ForwardPaperLedger):
    """Inactive executor boundary: validate Mayur's exact choice atomically.

    A future runtime must use this class plus verified source adapters. The base
    accounting library alone is not an authorized human-choice executor.
    """
    def validate_entry(self,db,account_id,command):
        if account_id!=ACCOUNT:raise ChoiceConflict("Pinned paper account required")
        source=PaperChoiceStore(self.database_url)
        choice=source.selected(db)
        selection=command.get("selection",{})
        if (not choice or selection.get("human_choice_id")!=choice["choice_id"] or
                selection.get("setup_receipt_id")!=choice["receipt_id"]):
            raise ChoiceConflict("A current explicit stock choice is required")
        if any(command.get(k)!=choice[k] for k in ("symbol","security_id","universe_revision")):
            raise ChoiceConflict("Cannot substitute another stock or universe")
        decision=instant(command["at"]);chosen=instant(choice["chosen_at"])
        if (decision<chosen or decision.date()!=chosen.date() or decision.time()>=time(11,30) or
                instant(command["known_at"])<chosen):
            raise ChoiceConflict("Choice must precede the prospective entry decision")
        if (Decimal(command["limit"])!=Decimal(choice["entry"]) or
                Decimal(command["stop"])!=Decimal(choice["initial_stop"]) or
                command["quantity"]>choice["quantity"]):
            raise ChoiceConflict("Selected entry/stop/size envelope changed")

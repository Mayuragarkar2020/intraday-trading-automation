"""Inactive paper ledger foundation; no feed, scheduler, API or broker integration.

The trusted future executor must establish source/session/signal eligibility and
compute fills. This module validates and journals its accounting commands only.
It does not certify caller-supplied signal evidence or create market fills.
"""
import copy
import hashlib
import json
import re
from datetime import datetime, time
from decimal import Decimal, ROUND_DOWN
from zoneinfo import ZoneInfo

from src.scan_store import ScanStore

IST = ZoneInfo("Asia/Kolkata")
CAPITAL = Decimal("980000")
RISK_CAP = Decimal("9800")
VERSION = "paper-ledger-v1"


def money(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,12}(\.\d{1,6})?", value):
        raise ValueError("Money must be a bounded nonnegative decimal string")
    return Decimal(value)


def instant(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Aware timestamp required")
    return result.astimezone(IST)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", value):
        raise ValueError("Bounded identifier required")
    return value


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def amount(value):
    return format(value, "f")


def quantity(value):
    if type(value) is not int or not 0 <= value <= 1000000:
        raise ValueError("Bounded integer quantity required")
    return value


def initial_state():
    return {"version": VERSION, "cash": amount(CAPITAL), "realised_pnl": "0",
            "fees": "0", "position": None, "orders": {}, "fills": [],
            "used_entry_dates": [], "last_at": None, "sequence": 0}


FIELDS = {
    "ENTRY_REQUEST": {"order_id", "signal_id", "universe_revision", "source_sha256",
                      "known_at", "quantity", "limit", "stop", "fee_budget"},
    "ENTRY_RESULT": {"order_id", "quantity", "price", "fee", "bar_open_at"},
    "EXIT_REQUEST": {"order_id", "reason"},
    "EXIT_RESULT": {"order_id", "quantity", "price", "fee"},
}


def transition(previous, command):
    """Pure transition. A failed command cannot mutate the caller's projection."""
    kind = command.get("kind")
    if kind not in FIELDS or set(command) != FIELDS[kind] | {"kind", "at"}:
        raise ValueError("Unknown command or fields")
    state = copy.deepcopy(previous)
    at = instant(command["at"])
    if state["last_at"] and at < instant(state["last_at"]):
        raise ValueError("Ledger clock moved backwards")
    order_id = identifier(command["order_id"])
    orders = state["orders"]
    cash = Decimal(state["cash"])
    position = state["position"]
    if kind == "ENTRY_REQUEST":
        if position or any(o["status"] == "PENDING" for o in orders.values()):
            raise ValueError("Exposure or pending order already exists")
        if at.date().isoformat() in state["used_entry_dates"]:
            raise ValueError("Daily filled entry already used")
        if not time(9,45) <= at.time() <= time(11,30):
            raise ValueError("Outside entry window")
        known = instant(command["known_at"])
        if known > at or known.date() != at.date():
            raise ValueError("Signal clock/session mismatch")
        identifier(command["signal_id"])
        identifier(command["universe_revision"])
        if any(o.get("signal_id") == command["signal_id"] for o in orders.values()):
            raise ValueError("Signal already bound to an entry order")
        if not re.fullmatch(r"[0-9a-f]{64}", command["source_sha256"]):
            raise ValueError("Source hash required")
        q = quantity(command["quantity"])
        limit, stop, budget = (money(command[k]) for k in ("limit", "stop", "fee_budget"))
        if not q or not 0 < stop < limit:
            raise ValueError("Positive long quantity and stop below limit required")
        if q * (limit - stop) + budget > RISK_CAP:
            raise ValueError("Planned risk exceeds cap")
        if q * limit + budget > cash:
            raise ValueError("Insufficient unlevered cash")
        if order_id in orders:
            raise ValueError("Order identity already exists")
        orders[order_id] = {**command, "side": "BUY", "status": "PENDING",
                            "filled": 0, "session_date": at.date().isoformat()}
    elif kind == "ENTRY_RESULT":
        order = orders.get(order_id)
        if not order or order["side"] != "BUY" or order["status"] != "PENDING":
            raise ValueError("Pending entry required")
        q = quantity(command["quantity"])
        price, fee = money(command["price"]), money(command["fee"])
        opened = instant(command["bar_open_at"])
        if (opened <= instant(order["known_at"]) or opened < instant(order["at"])
                or opened > at or opened.date().isoformat() != order["session_date"]
                or at.date() != opened.date()
                or not time(9,45) <= opened.time() <= time(11,30)):
            raise ValueError("Later same-session eligible bar required")
        if q > order["quantity"] or (not q and (price or fee)):
            raise ValueError("Invalid IOC result")
        if q and (price <= 0 or price > money(order["limit"]) or price <= money(order["stop"])):
            raise ValueError("Fill outside entry risk envelope")
        if fee > money(order["fee_budget"]) or q * price + fee > cash:
            raise ValueError("Fee budget or cash exceeded")
        order.update(status="FILLED" if q == order["quantity"] else "IOC_CANCELLED", filled=q)
        if q:
            cash -= q * price + fee
            position = {"entry_order_id": order_id, "quantity": q, "entry_price": amount(price),
                        "remaining_entry_fee": amount(fee), "stop": order["stop"]}
            state["used_entry_dates"].append(order["session_date"])
            state["fees"] = amount(Decimal(state["fees"]) + fee)
            state["fills"].append({**command, "side": "BUY"})
    elif kind == "EXIT_REQUEST":
        if not position or any(o["status"] == "PENDING" for o in orders.values()):
            raise ValueError("Open exposure without pending order required")
        if order_id in orders or command["reason"] not in {"STOP", "EMA10", "FLATTEN"}:
            raise ValueError("Invalid exit identity or reason")
        orders[order_id] = {**command, "side": "SELL", "status": "PENDING",
                            "quantity": position["quantity"], "filled": 0}
    else:
        order = orders.get(order_id)
        if not order or order["side"] != "SELL" or order["status"] != "PENDING" or not position:
            raise ValueError("Pending exit and exposure required")
        q = quantity(command["quantity"])
        price, fee = money(command["price"]), money(command["fee"])
        if q > position["quantity"] or (q and price <= 0) or (not q and (price or fee)):
            raise ValueError("Invalid exit result")
        # Zero/rejected exits and partial exits keep the remaining exposure pending.
        if q:
            old_q = position["quantity"]
            entry_fee = Decimal(position["remaining_entry_fee"])
            allocated = entry_fee if q == old_q else (entry_fee * q / old_q).quantize(
                Decimal("0.000001"), rounding=ROUND_DOWN)
            realised = q * (price - Decimal(position["entry_price"])) - fee - allocated
            cash += q * price - fee
            position["quantity"] -= q
            position["remaining_entry_fee"] = amount(entry_fee - allocated)
            state["realised_pnl"] = amount(Decimal(state["realised_pnl"]) + realised)
            state["fees"] = amount(Decimal(state["fees"]) + fee)
            state["fills"].append({**command, "side": "SELL"})
            order["filled"] += q
            if not position["quantity"]:
                position = None
                order["status"] = "FILLED"
    state.update(cash=amount(cash), position=position, last_at=at.isoformat(),
                 sequence=state["sequence"] + 1)
    basis = (Decimal(position["entry_price"]) * position["quantity"] +
             Decimal(position["remaining_entry_fee"])) if position else Decimal(0)
    if cash + basis != CAPITAL + Decimal(state["realised_pnl"]):
        raise ValueError("Cash/position/P&L reconciliation failed")
    return state


class ForwardPaperLedger(ScanStore):
    """Account projection and immutable command/result journal commit together.

    One global PostgreSQL writer lock deliberately serializes this initial small
    ledger. SQLite is a test backend. Nothing initializes on import/deployment.
    """
    def initialize(self):
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031010)")
            db.execute("""CREATE TABLE IF NOT EXISTS forward_paper_accounts (
                account_id TEXT PRIMARY KEY, payload TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS forward_paper_events (
                account_id TEXT NOT NULL, event_id TEXT NOT NULL, sequence INTEGER NOT NULL,
                command TEXT NOT NULL, result TEXT NOT NULL,
                PRIMARY KEY(account_id,event_id), UNIQUE(account_id,sequence))""")

    def apply(self, account_id, event_id, command):
        identifier(account_id)
        identifier(event_id)
        encoded = encode(command)
        if len(encoded) > 8192:
            raise ValueError("Command too large")
        self.initialize()
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031011)")
            else:
                db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT command,result FROM forward_paper_events WHERE account_id="+p+
                             " AND event_id="+p, (account_id,event_id)).fetchone()
            if old:
                if old[0] != encoded:
                    raise ValueError("Event identity conflict")
                return {"status": "ALREADY_APPLIED", "state": json.loads(old[1])}
            row = db.execute("SELECT payload FROM forward_paper_accounts WHERE account_id="+p,
                             (account_id,)).fetchone()
            state = transition(json.loads(row[0]) if row else initial_state(), command)
            result = encode(state)
            db.execute("INSERT INTO forward_paper_events VALUES ("+",".join([p]*5)+")",
                       (account_id,event_id,state["sequence"],encoded,result))
            db.execute("INSERT INTO forward_paper_accounts VALUES ("+p+","+p+") "
                       "ON CONFLICT(account_id) DO UPDATE SET payload=excluded.payload", (account_id,result))
            return {"status": "APPLIED", "state": state}

    def read(self, account_id):
        identifier(account_id)
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            row = db.execute("SELECT payload FROM forward_paper_accounts WHERE account_id="+p,
                             (account_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def audit(self, account_id):
        """Rebuild from commands and compare every immutable recorded projection."""
        identifier(account_id)
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            # Lock gives one consistent audit view while workers write.
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031011)")
            else:
                db.execute("BEGIN IMMEDIATE")
            events = db.execute("SELECT sequence,command,result FROM forward_paper_events WHERE account_id="+
                                p+" ORDER BY sequence", (account_id,)).fetchall()
            row = db.execute("SELECT payload FROM forward_paper_accounts WHERE account_id="+p,
                             (account_id,)).fetchone()
            state = initial_state()
            for sequence, command, result in events:
                state = transition(state, json.loads(command))
                if sequence != state["sequence"] or encode(state) != result:
                    raise ValueError("Journal reconciliation failed")
            if not events or not row or encode(state) != row[0]:
                raise ValueError("Account reconciliation failed")
        return {"status": "RECONCILED", "event_count": len(events),
                "state_sha256": hashlib.sha256(encode(state).encode()).hexdigest()}


"""Inactive, atomic receipt-time paper simulation. No API/cron/broker imports.

The future trusted adapter must establish the source attestations. They are not
proof merely because a caller sets them. Current research signals remain held.
Fills use the next timely completed-bar CLOSE at receipt time, never a past open
or an earlier intrabar extremum. This conservative model differs from replay.
"""
import copy
import hashlib
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_FLOOR
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.forward_paper_ledger import amount, encode, instant, money, transition

D = Decimal
FLAGS = ("timestamp_verified", "session_contract_verified", "reference_prices_verified",
         "breakout_receipts_verified")


class PaperBar(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    kind: Literal["SIMULATED_BAR"] = "SIMULATED_BAR"
    at: str
    close_at: str
    symbol: str = Field(pattern=r"^[A-Z0-9&._-]{2,30}$")
    security_id: str = Field(pattern=r"^[0-9]{1,12}$")
    universe_revision: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    close: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    high: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    low: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    # Derived EMA uses Decimal arithmetic and need not lie on the price grid.
    # Preserve its precision so close<EMA decisions do not change by rounding.
    ema10: Decimal = Field(gt=0, le=10000000, max_digits=40, decimal_places=30)
    volume: int = Field(ge=0, le=1000000000000, strict=True)
    participation_pct: Decimal = Field(gt=0, le=10, max_digits=12, decimal_places=6)
    slippage_bps: Decimal = Field(ge=0, le=100, max_digits=12, decimal_places=6)
    tick_size: Decimal = Field(ge=D("0.0001"), le=10, max_digits=12, decimal_places=6)
    reject_entry: bool = False
    reject_exit: bool = False
    reject_stop_change: bool = False
    timestamp_verified: bool = False
    session_contract_verified: bool = False
    reference_prices_verified: bool = False
    breakout_receipts_verified: bool = False

    @model_validator(mode="after")
    def validate_bar(self):
        at, close = instant(self.at), instant(self.close_at)
        if (close.second or close.microsecond or close.minute % 5 or
                not time(9,20) <= close.time() <= time(15,15) or
                close.date() != at.date() or not timedelta() <= at-close <= timedelta(seconds=90)):
            raise ValueError("Timely same-session completed five-minute receipt required")
        if not self.low <= self.close <= self.high:
            raise ValueError("Invalid OHLC range")
        return self


def manage_bar(previous, command):
    """One event journals all derived fills, stops, exits and deadline state."""
    b = PaperBar.model_validate(command)
    if not all(getattr(b, flag) for flag in FLAGS):
        raise ValueError("Source verification required")
    s = copy.deepcopy(previous)
    at, close = instant(b.at), instant(b.close_at)
    if s["last_at"] and at < instant(s["last_at"]):
        raise ValueError("Ledger clock moved backwards")
    pending = [o for o in s["orders"].values() if o["status"] == "PENDING"]
    position = s["position"]
    entry = (s["orders"][position["entry_order_id"]] if position else
             next((o for o in pending if o["side"] == "BUY"), None))
    if not entry or not all(entry.get(k) == getattr(b,k) for k in
                            ("symbol", "security_id", "universe_revision")):
        raise ValueError("Bound entry/instrument/universe required")
    if not all(entry.get("selection", {}).get("source_attestations", {}).get(k) is True for k in FLAGS):
        raise ValueError("Verified selection required")
    if instant(entry["at"]).date() != at.date():
        raise ValueError("Cross-session paper data")
    if s.get("management", {}).get("entry_order_id") != entry["order_id"]:
        s["management"] = {"entry_order_id":entry["order_id"]}
    previous_close = s.get("management", {}).get("last_close_at")
    if previous_close and close <= instant(previous_close):
        raise ValueError("Duplicate or out-of-order completed bar")
    # A gap may request protective exits, but cannot use missed bars for fills.
    gap = bool(previous_close and close-instant(previous_close) != timedelta(minutes=5))
    m = s.setdefault("management", {})
    m.update(last_close_at=close.isoformat(), source_sha256=b.source_sha256,
             fill_model="NEXT_TIMELY_CLOSE_AT_RECEIPT", gap=gap)
    capacity = int((D(b.volume)*b.participation_pct/100).to_integral_value(rounding=ROUND_FLOOR))
    cost = money(entry["selection"]["round_trip_cost_per_share"])
    if cost/2 != (cost/2).quantize(D("0.000001")):
        raise ValueError("Cost assumption must support six-decimal half-share fees")
    slip = b.slippage_bps/10000
    def price(buy):
        from decimal import ROUND_CEILING
        raw = b.close * (1+slip if buy else 1-slip)
        return (raw/b.tick_size).to_integral_value(rounding=ROUND_CEILING if buy else ROUND_FLOOR)*b.tick_size
    def apply(command):
        nonlocal s
        s = transition(s, command)
    def request(reason):
        oid = "exit_"+hashlib.sha256(encode([entry["order_id"],reason,b.close_at]).encode()).hexdigest()
        apply(dict(kind="EXIT_REQUEST",at=b.at,order_id=oid,reason=reason))
    deadline = datetime.combine(at.date(),time(15),tzinfo=at.tzinfo)
    if position and at > deadline:
        m["closure_deadline_breached"] = True
    if position and pending:
        order = pending[0]
        # Existing sell requests only; an exit decision made on this bar cannot
        # fill using the same bar. Rejected and partial exits retain exposure.
        if order["side"] != "SELL":
            raise ValueError("Unexpected pending order with exposure")
        px = price(False)
        q = min(position["quantity"],capacity) if (instant(order["at"])<close and not gap
            and not b.reject_exit and b.low <= px <= b.high) else 0
        apply(dict(kind="EXIT_RESULT",at=b.at,order_id=order["order_id"],
                   quantity=q,price=amount(px) if q else "0",fee=amount(cost*q/2)))
    elif position:
        if at.time() >= time(14,50):
            request("FLATTEN")
        elif b.low <= money(position["stop"]):
            request("STOP")
        elif b.close < b.ema10:
            request("EMA10")  # active before 1.5R too
        elif not gap:
            initial = money(entry["stop"])
            if b.high >= money(position["entry_price"])+D("1.5")*(money(position["entry_price"])-initial):
                if b.reject_stop_change:
                    m["stop_change_status"] = "REJECTED_KEEP_PREVIOUS_STOP"
                else:
                    # Only future bars consult this new stop. Initial stop remains
                    # immutable in the entry order for the original R calculation.
                    target=money(position["entry_price"])+cost
                    if entry["selection"].get("cost_breakeven_includes_execution") is True:
                        from decimal import ROUND_CEILING
                        target=((target+b.tick_size)/(1-slip)/b.tick_size).to_integral_value(rounding=ROUND_CEILING)*b.tick_size
                    s["position"]["stop"] = amount(max(money(position["stop"]),target))
                    m["stop_change_status"] = "COST_BREAKEVEN_NEXT_BAR"
    elif pending:
        order = pending[0]
        opened = close-timedelta(minutes=5)
        if at.time() > time(11,30):
            order["status"] = "IOC_CANCELLED"
            order["cancel_reason"] = "ENTRY_WINDOW_CLOSED"
            s["management"] = m
            s.update(last_at=at.isoformat(),sequence=previous["sequence"]+1)
            return s
        if opened <= instant(order["known_at"]):
            raise ValueError("Entry requires a prospective later bar")
        px = price(True)
        eligible = (not gap and not b.reject_entry and at.time() <= time(11,30)
                    and b.low > money(order["stop"]) and b.high >= money(order["limit"])
                    and money(order["stop"]) < px <= money(order["limit"])
                    and b.low <= px <= b.high)
        q = min(order["quantity"],capacity) if eligible else 0
        apply(dict(kind="ENTRY_RESULT",at=b.at,order_id=order["order_id"],bar_open_at=opened.isoformat(),
                   quantity=q,price=amount(px) if q else "0",fee=amount(cost*q/2)))
    # Nested transitions copy state, so reattach the derived management fields.
    s["management"] = m
    if s["position"] and at >= deadline:
        m["closure_deadline_breached"] = True
    s.update(last_at=at.isoformat(),sequence=previous["sequence"]+1)
    return s


def manage_clock(previous, command):
    """Feed-independent requests/breach accounting. A clock never creates fills."""
    if set(command) != {"kind","at"}:
        raise ValueError("Unknown paper clock fields")
    at = instant(command["at"])
    if previous["last_at"] and at < instant(previous["last_at"]):
        raise ValueError("Ledger clock moved backwards")
    s = copy.deepcopy(previous)
    position = s["position"]
    pending = [o for o in s["orders"].values() if o["status"] == "PENDING"]
    for order in pending:
        if order["side"] == "BUY" and (at.date() > instant(order["at"]).date() or at.time() >= time(11,30)):
            order.update(status="IOC_CANCELLED",cancel_reason="ENTRY_WINDOW_CLOSED")
    if position:
        entry = s["orders"][position["entry_order_id"]]
        deadline = datetime.combine(instant(entry["at"]).date(),time(15),tzinfo=at.tzinfo)
        m = s.setdefault("management", {})
        if at >= deadline:
            m["closure_deadline_breached"] = True
        if at >= deadline-timedelta(minutes=10) and not pending:
            oid = "flatten_"+hashlib.sha256(entry["order_id"].encode()).hexdigest()
            s = transition(s,dict(kind="EXIT_REQUEST",at=command["at"],order_id=oid,reason="FLATTEN"))
    s.update(last_at=at.isoformat(),sequence=previous["sequence"]+1)
    return s


def simulate_paper_bar(ledger, account_id, value):
    b = PaperBar.model_validate(value)
    if not all(getattr(b,flag) for flag in FLAGS):
        return {"status":"HELD_SOURCE_VERIFICATION", "execution_enabled":False,
                "paper_runtime_enabled":False}
    command = b.model_dump(mode="json")
    eid = "bar_"+hashlib.sha256(encode([b.symbol,b.security_id,instant(b.close_at).isoformat()]).encode()).hexdigest()
    result = ledger.apply(account_id,eid,command)
    return {**result,"execution_enabled":False,"paper_runtime_enabled":False}

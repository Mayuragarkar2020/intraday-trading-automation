"""Deterministic OHLC replay with no network or broker dependencies.

All timestamps are completed 5m bar closes. An order is eligible only after
its signal was known. Intrabar sequencing is unknowable: stop/invalidation
wins, new stops take effect on the next bar, EMA exits on the next open.
"""
import hashlib
import json
from dataclasses import replace
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from zoneinfo import ZoneInfo
from src.candle_session import parse_close, ensure_ordered_session
from src.market_schedule import HOLIDAYS_2026
from src.paper_models import ReplayRequest
from src.risk_engine import RiskPolicy, size_long
from src.trade_manager import open_long, on_completed_candle

D = Decimal
IST = ZoneInfo("Asia/Kolkata")
VERSION = "paper-replay-2-deadline"
FLATTEN_LEAD_MINUTES = 10

def text_number(value):
    return format(value, "f")

def _clock(value):
    try:
        parsed = time.fromisoformat(value)
    except ValueError:
        raise ValueError("Invalid replay window") from None
    if len(value) != 5 or parsed.second or parsed.tzinfo or parsed.minute % 5:
        raise ValueError("Replay windows require HH:MM aligned to five minutes")
    return parsed

def replay(request: ReplayRequest, *, as_of=None):
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Aware replay clock required")
    start, end, flatten = map(_clock, (request.entry_start, request.entry_end, request.force_exit))
    if not time(9,15) <= start < end < flatten <= time(15,0):
        raise ValueError("Require session open <= entry start < entry end < closure deadline <= 15:00")
    flatten_request = (datetime.combine(now.date(), flatten) - timedelta(minutes=FLATTEN_LEAD_MINUTES)).time()
    if end > flatten_request:
        raise ValueError("Entry window must end before the ten-minute flatten lead")
    ids, dates, events = set(), set(), []
    for plan in request.plans:
        if plan.plan_id in ids:
            raise ValueError("Duplicate plan ID")
        ids.add(plan.plan_id)
        known = parse_close(plan.known_at)
        dates.add(known.date())
        if known.year != 2026 or known.date().isoformat() in HOLIDAYS_2026:
            raise ValueError("Replay date is outside the reviewed normal-session calendar")
        if known > now or plan.stop >= plan.trigger:
            raise ValueError("Future signal or invalid long stop")
        ensure_ordered_session([b.time for b in plan.bars])
        if parse_close(plan.bars[0].time) != known + timedelta(minutes=5):
            raise ValueError("Replay must begin with the bar immediately after signal close")
        for bar in plan.bars:
            close_time = parse_close(bar.time)
            if close_time.date() != known.date() or close_time > now:
                raise ValueError("Future or cross-session replay bar")
            if not bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high:
                raise ValueError("Invalid OHLC values")
            events.append((close_time, plan.plan_id, plan, bar))
    if len(dates) != 1:
        raise ValueError("One session per replay; use separate runs for different dates")
    canonical = request.model_dump_json()
    digest = hashlib.sha256((VERSION + "\n" + canonical).encode()).hexdigest()
    policy = RiskPolicy()
    cash, position, realized = policy.capital, None, D(0)
    entered, peak, max_dd, last_equity = 0, policy.capital, D(0), policy.capital
    cost = request.round_trip_cost_per_share
    slip = request.slippage_bps / D(10000)
    states = {p.plan_id: {"plan_id":p.plan_id,"symbol":p.symbol,"state":"PENDING","reason":"WAITING_FOR_BREAKOUT"} for p in request.plans}
    ledger, journal, curve, notices = [], [], [], []

    def record(kind, plan, bar, **extra):
        row = {"sequence":len(ledger)+1,"kind":kind,"plan_id":plan.plan_id,
               "symbol":plan.symbol,"bar_close":bar.time, **extra}
        ledger.append(row)

    def fill_price(price, tick, buy=False):
        price *= D(1)+slip if buy else D(1)-slip
        return (price/tick).to_integral_value(rounding=ROUND_CEILING if buy else ROUND_FLOOR)*tick

    def sell(plan, bar, base, reason, capacity):
        nonlocal cash, position, realized
        price = fill_price(base, plan.tick_size)
        if not bar.can_fill or bar.reject_exit or capacity <= 0 or not bar.low <= price <= bar.high:
            record("EXIT_UNFILLED",plan,bar,reason=reason,detail="REJECTED" if bar.reject_exit else "NO_EXECUTABLE_LIQUIDITY")
            return
        qty = min(position["remaining"], capacity)
        fee = cost*qty/D(2)
        cash += price*qty-fee
        position["remaining"] -= qty
        position["exit_value"] += price*qty
        position["fees"] += fee
        # Next-open simulation has an explicit price instant. For intrabar stops,
        # use the close as a conservative latest fill time; no tick path is known.
        fill_at = parse_close(bar.time) - (timedelta(minutes=5) if position["pending_exit"] else timedelta())
        record("EXIT_FILL",plan,bar,reason=reason,quantity=qty,price=text_number(price),fee=text_number(fee),fill_at=fill_at.isoformat(),timing="NEXT_OPEN" if position["pending_exit"] else "STOP_WITHIN_BAR")
        if position["remaining"]:
            position["pending_exit"] = reason
            return
        net = position["exit_value"]-position["entry"]*position["quantity"]-position["fees"]
        realized += net
        journal.append({"plan_id":plan.plan_id,"symbol":plan.symbol,
            "entry":text_number(position["entry"]),"exit_average":text_number(position["exit_value"]/position["quantity"]),
            "quantity":position["quantity"],"entry_bar_close":position["entered_at"],"exit_bar_close":bar.time,
            "exit_reason":reason,"exit_fill_at":fill_at.isoformat(),
            "closure_deadline_breached":fill_at.time()>flatten,
            "fees":text_number(position["fees"]),"net_pnl":text_number(net),
            "planned_risk":text_number(position["risk"]),"net_r":text_number(net/position["risk"]),
            "risk_budget_breached":-net>policy.capital*policy.max_risk_fraction})
        states[plan.plan_id].update(state="CLOSED",reason=reason)
        position = None

    for when, _, plan, bar in sorted(events, key=lambda e:(e[0],e[1])):
        state = states[plan.plan_id]
        opened = when-timedelta(minutes=5)
        capacity = int((D(bar.volume)*request.participation_pct/D(100)).to_integral_value(rounding=ROUND_FLOOR))
        if position and position["plan_id"] == plan.plan_id:
            position["mark"] = bar.close
            stop_hit = bar.low <= position["stop"]
            reason = position["pending_exit"] or ("SESSION_FLATTEN" if opened.time()>=flatten_request else "STOP" if stop_hit else None)
            if reason:
                # An already pending market exit/flatten uses next open; stops gap down at open.
                base = bar.open if position["pending_exit"] or reason=="SESSION_FLATTEN" else min(bar.open,position["stop"])
                position["pending_exit"] = reason if position["pending_exit"] or reason=="SESSION_FLATTEN" else None
                sell(plan,bar,base,reason,capacity)
                if position:
                    position["pending_exit"] = reason
            elif opened.time() < flatten_request:
                managed, action = on_completed_candle(position["managed"],bar.high,bar.low,bar.close,bar.ema10)
                position["managed"] = managed
                if action == "REQUEST_EXIT_EMA10_CLOSE":
                    position["pending_exit"] = "EMA10_CLOSE"
                    record("EXIT_REQUEST",plan,bar,reason="EMA10_CLOSE_NEXT_OPEN")
                elif action == "REQUEST_STOP_TO_COST_BREAKEVEN":
                    if bar.reject_stop_change:
                        position["managed"] = replace(managed,break_even_requested=False)
                        record("STOP_CHANGE_REJECTED",plan,bar,reason="KEEP_PREVIOUS_STOP")
                    else:
                        position["stop"] = max(position["stop"],position["entry"]+cost)
                        record("STOP_CHANGED",plan,bar,stop=text_number(position["stop"]),effective="NEXT_BAR")
        elif state["state"] == "PENDING":
            reason = None
            if plan.reference_status != "RESEARCH_ONLY": reason="REFERENCE_HELD_OR_EXCLUDED"
            elif plan.price_band in (2,5): reason="LOW_PRICE_BAND"
            elif not D(300)<=plan.trigger<=D(5000): reason="PRICE_OUTSIDE_UNIVERSE_RANGE"
            elif opened.time() >= end: reason="ENTRY_WINDOW_CLOSED"
            elif entered >= policy.max_trades_per_day: reason="DAILY_TRADE_LIMIT"
            elif position: reason="POSITION_ALREADY_OPEN"
            elif bar.low <= plan.stop: reason="SETUP_INVALIDATED_BEFORE_ENTRY"
            if reason:
                state.update(state="REJECTED",reason=reason)
                record("ENTRY_REJECTED",plan,bar,reason=reason)
            elif opened.time()>=start and bar.high>=plan.trigger:
                price = fill_price(max(bar.open,plan.trigger),plan.tick_size,True)
                if bar.reject_entry:
                    state.update(state="REJECTED",reason="SIMULATED_ENTRY_REJECTION")
                    record("ENTRY_REJECTED",plan,bar,reason=state["reason"])
                elif not bar.can_fill or capacity<=0 or not bar.low<=price<=bar.high:
                    record("ENTRY_UNFILLED",plan,bar,reason="NO_EXECUTABLE_LIQUIDITY")
                else:
                    sizing = size_long(price,plan.stop,cost+plan.stop*slip+plan.tick_size,entered,policy)
                    affordable = int((cash/(price+cost/D(2))).to_integral_value(rounding=ROUND_FLOOR))
                    desired = min(sizing.quantity,affordable)
                    qty = min(desired,capacity)
                    if qty<=0:
                        state.update(state="REJECTED",reason="CAPITAL_OR_RISK_LIMIT")
                        record("ENTRY_REJECTED",plan,bar,reason=state["reason"])
                    else:
                        fee = cost*qty/D(2)
                        cash -= price*qty+fee
                        entered += 1
                        position = {"plan_id":plan.plan_id,"entry":price,"stop":plan.stop,"quantity":qty,
                            "remaining":qty,"entered_at":bar.time,"fees":fee,"exit_value":D(0),
                            "risk":(price-plan.stop+cost+plan.stop*slip+plan.tick_size)*qty,
                            "mark":bar.close,"pending_exit":None,"managed":open_long(price,plan.stop,qty,cost)}
                        state.update(state="OPEN",reason="PARTIAL_ENTRY_IOC_REMAINDER_CANCELLED" if qty<desired else "ENTRY_FILLED")
                        record("ENTRY_FILL",plan,bar,quantity=qty,requested_quantity=desired,price=text_number(price),fee=text_number(fee),timing="INTRABAR_SEQUENCE_UNKNOWN")
                        if qty<desired: record("ENTRY_REMAINDER_CANCELLED",plan,bar,quantity=desired-qty,reason="IOC_PARTIAL_FILL")
                        # Do not use pre-entry intrabar extrema for trailing stops or EMA decisions.
        equity = cash+(position["mark"]*position["remaining"]-cost*position["remaining"]/D(2) if position else D(0))
        peak=max(peak,equity)
        max_dd=max(max_dd,(peak-equity)/peak)
        last_equity=equity
        curve.append({"bar_close":bar.time,"plan_id":plan.plan_id,"equity":text_number(equity)})
    for state in states.values():
        if state["state"] == "PENDING": state.update(state="EXPIRED",reason="REPLAY_ENDED_WITHOUT_FILL")
    open_position = None
    if position:
        notices.append("OPEN_POSITION_UNRESOLVED: replay ended without an executable exit; no closing fill was invented.")
        open_position={k:(text_number(v) if isinstance(v,D) else v) for k,v in position.items() if k!="managed"}
    if any(r["kind"] in ("EXIT_UNFILLED","STOP_CHANGE_REJECTED") for r in ledger):
        notices.append("Execution or stop-change failures occurred; inspect the event ledger.")
    deadline = datetime.combine(next(iter(dates)),flatten,tzinfo=IST)
    deadline_breached = any(t["closure_deadline_breached"] for t in journal) or bool(position and now >= deadline)
    if deadline_breached:
        notices.append("CLOSURE_DEADLINE_BREACH: exposure was not confirmed closed by the deadline; late recovery does not erase the breach.")
    wins=sum(D(t["net_pnl"])>0 for t in journal)
    # A partially exited trade has realised P&L even before its journal row closes.
    partial_realized=D(0)
    unrealized=D(0)
    if position:
        exited=position["quantity"]-position["remaining"]
        partial_realized=position["exit_value"]-(position["entry"]+cost)*exited
        unrealized=(position["mark"]-position["entry"]-cost)*position["remaining"]
    return {"run_id":digest,"engine_version":VERSION,"mode":"PAPER_REPLAY_ONLY","execution_enabled":False,
        "live":False,"source":request.source,"label":request.label,"session":next(iter(dates)).isoformat(),
        "input_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
        "assumptions":{"capital":text_number(policy.capital),"risk_fraction":text_number(policy.max_risk_fraction),
            "max_trades_per_day":policy.max_trades_per_day,"entry_start":request.entry_start,"entry_end":request.entry_end,
            "force_exit":request.force_exit,"force_exit_semantics":"COMPLETED_CLOSURE_DEADLINE",
            "flatten_request_at":flatten_request.isoformat(timespec="minutes"),
            "flatten_lead_minutes":FLATTEN_LEAD_MINUTES,
            "round_trip_cost_per_share":text_number(cost),"slippage_bps":text_number(request.slippage_bps),
            "participation_pct":text_number(request.participation_pct),"signal_origin":"EXPLICIT_TEST_PLAN_NOT_AUTOMATIC_SCANNER",
            "fill_model":"ADVERSE_SLIPPAGE_TICK_ROUNDING_VOLUME_CAP_STOP_FIRST_IOC_ENTRY",
            "calendar":"NORMAL_2026_SESSIONS_ONLY","eligibility_verified":False},
        "summary":{"entries":entered,"closed_trades":len(journal),"wins":wins,"net_realized_pnl":text_number(realized+partial_realized),
            "closed_trade_net_pnl":text_number(realized),"unrealized_pnl_estimate":text_number(unrealized),
            "cash":text_number(cash),"ending_equity_estimate":text_number(last_equity),"max_drawdown_pct_estimate":text_number(max_dd*100),
            "open_positions":int(position is not None),"complete":position is None,
            "closure_deadline":deadline.isoformat(),"closure_deadline_breached":deadline_breached,
            "risk_breaches":sum(t["risk_budget_breached"] for t in journal)},
        "orders":list(states.values()),"trades":journal,"events":ledger,"equity_curve":curve,"open_position":open_position,
        "warnings":["Simulation only. Declared reference status, OHLCV and EMA inputs are unverified.",
            "OHLC bars cannot establish queue priority, tick path or actual broker fills; volume participation is an estimate.",
            "Costs and windows are explicit research assumptions, not a verified broker fee schedule or a live-trading approval.",
            "Gap losses may exceed planned risk; incomplete exits remain open. Passing scenarios does not prove profitability.",*notices]}

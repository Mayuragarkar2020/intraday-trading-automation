"""Inactive persisted-source bridge. No client source flags or uploaded prices.

Current receipt/version gates are false. Reading timely research evidence cannot
promote them. This module connects a future independently verified receipt stream
to reservations and the durable manager; it does not supply that verifier.
"""
from datetime import timedelta, time
from decimal import Decimal
import hashlib
import json
import re

from src.forward_paper_ledger import encode, instant
from src.paper_entry_selection import EntryBatch, reserve_paper_entry
from src.paper_trade_management import simulate_paper_bar

FLAGS=("timestamp_verified","session_contract_verified","reference_prices_verified",
       "breakout_receipts_verified")


def held(status):
    return {"status":status,"execution_enabled":False,"paper_runtime_enabled":False}


def read_universe(store,revision,target,decision):
    p="%s" if store.postgres else "?"
    with store.connection() as db:
        row=db.execute("SELECT target_date,asof_date,created_at,payload,evidence FROM "
                       "universe_research_snapshots WHERE revision="+p,(revision,)).fetchone()
    if not row or hashlib.sha256((row[3]+"\n"+row[4]).encode()).hexdigest()!=revision:
        raise ValueError("Immutable universe required")
    snapshot=json.loads(row[3])
    if (row[0]!=target or snapshot["target_date"]!=target or snapshot["asof_date"]!=row[1]
            or instant(row[2]).date().isoformat()!=target or instant(row[2])>decision):
        raise ValueError("Same-day universe publication required")
    return snapshot


def receipt_pair(store,setup_id,breakout_id,decision):
    """The store validates hash/candle/reference integrity before returning data."""
    setup,breakout=store.read(setup_id),store.read(breakout_id)
    if not setup or not breakout: raise ValueError("Persisted setup and breakout required")
    identity=("symbol","security_id","universe_revision","reference_sha256")
    if any(setup[k]!=breakout[k] for k in identity):
        raise ValueError("Setup/breakout identity mismatch")
    close=instant(breakout["candle_close"])
    start=close-timedelta(minutes=5)
    if (instant(setup["known_at"])>=start or instant(breakout["known_at"])>decision
            or not timedelta()<=decision-close<=timedelta(seconds=90)
            or instant(setup["known_at"]).date()!=close.date()):
        raise ValueError("Later breakout bar and timely prospective decision required")
    # Every bar after the setup must be present in the immutable latest receipt.
    tail=[b for b in breakout["candles"] if instant(b["time"])>instant(setup["candle_close"])]
    if (not tail or instant(tail[0]["time"])!=instant(setup["candle_close"])+timedelta(minutes=5)
            or instant(tail[-1]["time"])!=close):
        raise ValueError("Complete setup-to-breakout path required")
    if setup["scanner_result"]["status"]!="ARMED":
        return setup,breakout,None,"HELD_SETUP_NOT_ARMED"
    entry,stop=(Decimal(setup["scanner_result"][k]) for k in ("entry","stop"))
    if not entry.is_finite() or not stop.is_finite() or not entry>stop>0:
        raise ValueError("Valid stored setup prices required")
    if any(Decimal(b["low"])<=stop for b in tail):
        return setup,breakout,None,"HELD_SETUP_INVALIDATED"
    # Using a later bar's high after an earlier breakout would re-rank a signal
    # that was already known. Only the first eligible breakout is considered.
    eligible=[b for b in tail if instant(b["time"])-timedelta(minutes=5)>instant(setup["known_at"])]
    hits=[b for b in eligible if Decimal(b["high"])>=entry]
    if not hits or instant(hits[0]["time"])!=close:
        return setup,breakout,None,"HELD_NOT_FIRST_LATER_BREAKOUT"
    return setup,breakout,(entry,stop),None


def reserve_from_receipts(ledger,account_id,store,pairs,*,decision_at,round_trip_cost_per_share):
    """Pairs contain stored IDs only. No prices, ranking scores or flags accepted."""
    decision=instant(decision_at)
    if not isinstance(pairs,list) or not 1<=len(pairs)<=120:
        raise ValueError("Bounded receipt pairs required")
    candidates=[]
    interval=None
    seen=set()
    for pair in pairs:
        if not isinstance(pair,dict) or set(pair)!={"setup_id","breakout_id"}:
            raise ValueError("Stored receipt IDs only")
        if any(not isinstance(v,str) or not re.fullmatch(r"[a-f0-9]{64}",v) for v in pair.values()):
            raise ValueError("Receipt hash identities required")
        setup,breakout,prices,reason=receipt_pair(store,pair["setup_id"],pair["breakout_id"],decision)
        identity=(setup["symbol"],setup["security_id"])
        if identity in seen: raise ValueError("Duplicate receipt instrument")
        seen.add(identity)
        start=instant(breakout["candle_close"])-timedelta(minutes=5)
        if interval is not None and interval!=start: raise ValueError("Mixed breakout intervals")
        interval=start
        # Real current receipts always hold here. Timeliness is not clearance.
        if any(r.get(flag) is not True for r in (setup,breakout) for flag in FLAGS):
            return held("HELD_SOURCE_VERIFICATION")
        if any(r.get("receipt_status")!="TIMELY_RESEARCH_EVIDENCE" for r in (setup,breakout)):
            return held("HELD_SETUP_FIRST_SEEN")
        if reason: return held(reason)
        universe=read_universe(store,setup["universe_revision"],start.date().isoformat(),decision)
        if (universe.get("mode")!="VERIFIED_PAPER_UNIVERSE" or
                universe.get("calendar_completeness_verified") is not True or
                universe.get("restrictions_verified") is not True):
            return held("HELD_UNIVERSE_REFERENCE")
        rows=[r for r in universe["candidates"] if r.get("symbol")==setup["symbol"]]
        if len(rows)!=1 or str(rows[0].get("dhan_security_id"))!=setup["security_id"]:
            raise ValueError("Unique universe instrument required")
        row=rows[0]
        if (row.get("reference_review_status")!="VERIFIED" or not row.get("liquidity_pass")
                or row.get("mapping_status")!="UNIQUE" or
                row.get("reference_price_band") not in (10,20,"10","20","No Band")):
            return held("HELD_UNIVERSE_REFERENCE")
        candidates.append(dict(symbol=setup["symbol"],security_id=setup["security_id"],
            signal_id=hashlib.sha256(encode([pair["setup_id"],pair["breakout_id"]]).encode()).hexdigest(),
            source_sha256=breakout["current_sha256"],universe_revision=setup["universe_revision"],
            status="BREAKOUT_CONFIRMED",evidence_kind="COMPLETED_BAR_RECEIPT",
            setup_receipt_id=pair["setup_id"],breakout_receipt_id=pair["breakout_id"],
            setup_known_at=setup["known_at"],breakout_observed_at=breakout["known_at"],
            avg_turnover_20d_cr=row["metrics"]["avg_turnover_20d_cr"],
            entry_limit=str(prices[0]),initial_stop=str(prices[1])))
    batch_id=hashlib.sha256(encode(sorted((p["setup_id"],p["breakout_id"]) for p in pairs)).encode()).hexdigest()
    batch=EntryBatch.model_validate(dict(batch_id=batch_id,interval_start=interval.isoformat(),
        decision_at=decision.isoformat(),round_trip_cost_per_share=round_trip_cost_per_share,
        candidates=candidates,**{k:True for k in FLAGS}))
    return reserve_paper_entry(ledger,account_id,batch)


def manage_from_receipt(ledger,account_id,store,receipt_id,*,decision_at,
                        participation_pct,slippage_bps,tick_size):
    """Route one committed, independently cleared bar to receipt-time simulation."""
    receipt=store.read(receipt_id)
    if not receipt: raise ValueError("Persisted management receipt required")
    if any(receipt.get(flag) is not True for flag in FLAGS):
        return held("HELD_SOURCE_VERIFICATION")
    decision=instant(decision_at)
    close=instant(receipt["candle_close"])
    if instant(receipt["known_at"])>decision or not timedelta()<=decision-close<=timedelta(seconds=90):
        raise ValueError("Timely decision after committed receipt required")
    # Do not trust supplied EMA. Rebuild it using the existing retained source
    # cache/current candles and the exact source input fingerprint.
    from src.universe_scanner import prepare_history,candidate_from,digest
    from src.universe_receipts import canonical_candidate
    from src.run_forward_capture import CALENDAR
    from src.daily_universe_refresh import reference_dates_for
    from src.candle_pipeline import ema
    calendar=json.loads(CALENDAR.read_text())
    p="%s" if store.postgres else "?"
    with store.connection() as db:
        row=db.execute("SELECT payload FROM universe_scan_reference_cache WHERE revision="+p+
                       " AND security_id="+p,(receipt["universe_revision"],receipt["security_id"])).fetchone()
    if not row or digest(json.loads(row[0]))!=receipt["reference_sha256"]:
        raise ValueError("Management reference source mismatch")
    previous=prepare_history(json.loads(row[0]),decision,reference_dates_for(close.date().isoformat(),calendar))
    current=receipt["candles"]
    raw={"timestamp":[int(instant(b["time"]).timestamp())-300 for b in current],
         **{k:[b[k] for b in current] for k in ("open","high","low","close","volume")}}
    candidate=candidate_from(receipt["symbol"],previous,raw,decision,close)
    if hashlib.sha256(encode(canonical_candidate(candidate)).encode()).hexdigest()!=receipt["candidate_sha256"]:
        raise ValueError("Management candidate source mismatch")
    last=current[-1]
    value=dict(kind="SIMULATED_BAR",at=decision.isoformat(),close_at=close.isoformat(),
        symbol=receipt["symbol"],security_id=receipt["security_id"],
        universe_revision=receipt["universe_revision"],source_sha256=receipt["current_sha256"],
        close=last["close"],high=last["high"],low=last["low"],volume=last["volume"],
        ema10=str(ema([*candidate.ema_warmup_closes,*[b.close for b in candidate.completed_5m]],10)),
        participation_pct=participation_pct,slippage_bps=slippage_bps,tick_size=tick_size,
        **{k:True for k in FLAGS})
    return simulate_paper_bar(ledger,account_id,value)

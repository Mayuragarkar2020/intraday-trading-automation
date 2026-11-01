"""Opt-in full-pool receipt evidence. Research only; never order clearance.

Reference prices stay in the existing immutable cache. Each observation keeps
the exact normalized current candles, their first receipt times, scanner-input
hash and post-scan known time. Nothing imports or initializes this on the web.
"""
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
import re

from src.candle_input import BatchInput, CandidateInput, scan_batch
from src.candle_session import ensure_ordered_session
from src.forward_paper_ledger import encode, instant
from src.scan_store import ScanStore

VERSION = "universe-receipts-v1"


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def canonical_candidate(candidate):
    # Decimal spelling is not a candle revision (100 and 100.0 are identical).
    def canonical(value):
        if isinstance(value,dict): return {k:canonical(v) for k,v in value.items()}
        if isinstance(value,list): return [canonical(v) for v in value]
        if isinstance(value,str) and re.fullmatch(r"-?\d+(\.\d+)?",value):
            return format(Decimal(value).normalize(),"f")
        return value
    return canonical(candidate.model_dump(mode="json"))


class UniverseReceiptStore(ScanStore):
    def initialize(self):
        with self.connection() as db:
            if self.postgres: db.execute("SELECT pg_advisory_xact_lock(73031020)")
            db.execute("""CREATE TABLE IF NOT EXISTS universe_receipt_candles (
                symbol TEXT NOT NULL, security_id TEXT NOT NULL, candle_close TEXT NOT NULL,
                first_seen_at TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(symbol,security_id,candle_close))""")
            db.execute("""CREATE TABLE IF NOT EXISTS universe_receipt_signals (
                receipt_id TEXT PRIMARY KEY, payload TEXT NOT NULL, sha256 TEXT NOT NULL)""")

    def record(self,revision,security_id,candidate,reference_sha256,current_sha256,
               observed_at,*,clock):
        if not isinstance(candidate,CandidateInput): candidate=CandidateInput.model_validate(candidate)
        if (not re.fullmatch(r"[A-Z0-9&._-]{2,30}",candidate.symbol) or
                not re.fullmatch(r"[0-9]{1,12}",security_id) or
                any(not re.fullmatch(r"[a-f0-9]{64}",v) for v in
                    (revision,reference_sha256,current_sha256))):
            raise ValueError("Bounded receipt identity and hashes required")
        normalized=canonical_candidate(candidate)
        current=normalized["completed_5m"]
        if not 3 <= len(current) <= 72:
            raise ValueError("Bounded current session required")
        ensure_ordered_session([b["time"] for b in current])
        observed=instant(observed_at)
        close=instant(current[-1]["time"])
        if (any(instant(b["time"]).date()!=close.date() for b in current) or
                current[0]["time"][11:16]!="09:20" or observed.date()!=close.date() or
                not timedelta() <= observed-close <= timedelta(seconds=90)):
            raise ValueError("Timely complete current-session receipt required")
        # CandidateInput does not enforce all OHLC relationships itself.
        for b in candidate.completed_5m:
            if not b.low <= min(b.open,b.close) <= max(b.open,b.close) <= b.high:
                raise ValueError("Invalid current OHLC")
        identity=digest([VERSION,revision,candidate.symbol,security_id,close.isoformat()])
        fingerprint=digest([normalized,reference_sha256])
        self.initialize()
        p="%s" if self.postgres else "?"
        with self.connection() as db:
            if self.postgres: db.execute("SELECT pg_advisory_xact_lock(73031021)")
            else: db.execute("BEGIN IMMEDIATE")
            cached=db.execute("SELECT payload,sha256 FROM universe_scan_reference_cache WHERE revision="+
                              p+" AND security_id="+p,(revision,security_id)).fetchone()
            if not cached or cached[1]!=reference_sha256 or digest(json.loads(cached[0]))!=reference_sha256:
                raise ValueError("Immutable reference cache required")
            # Rebuild indicators from the retained reference cache/current bars;
            # caller-supplied 15m aggregates and EMA warmup cannot become evidence.
            from src.universe_scanner import prepare_history, candidate_from
            from src.daily_universe_refresh import reference_dates_for
            from src.run_forward_capture import CALENDAR
            calendar=json.loads(CALENDAR.read_text())
            target=close.date().isoformat()
            if target not in calendar["sessions"] or not calendar["earliest_target"] <= target <= calendar["latest_target"]:
                raise ValueError("Reviewed receipt session required")
            previous=prepare_history(json.loads(cached[0]),observed,reference_dates_for(target,calendar))
            raw={"timestamp":[int(instant(b["time"]).timestamp())-300 for b in current],
                 **{k:[b[k] for b in current] for k in ("open","high","low","close","volume")}}
            rebuilt=candidate_from(candidate.symbol,previous,raw,observed,close)
            if canonical_candidate(rebuilt)!=normalized:
                raise ValueError("Candidate does not match retained source inputs")
            old=db.execute("SELECT payload,sha256 FROM universe_receipt_signals WHERE receipt_id="+p,
                           (identity,)).fetchone()
            if old:
                saved=json.loads(old[0])
                if digest(saved)!=old[1] or saved["input_fingerprint"]!=fingerprint:
                    raise ValueError("Immutable receipt conflict")
                return {"status":"ALREADY_RECORDED","receipt":saved}
            first=[]
            for bar in current:
                encoded=encode(bar)
                key=(candidate.symbol,security_id,bar["time"])
                saved=db.execute("SELECT first_seen_at,payload FROM universe_receipt_candles WHERE symbol="+
                    p+" AND security_id="+p+" AND candle_close="+p,key).fetchone()
                if saved and (saved[1]!=encoded or instant(saved[0])>observed):
                    raise ValueError("Candle revision or backwards receipt")
                if not saved:
                    db.execute("INSERT INTO universe_receipt_candles VALUES ("+",".join([p]*5)+")",
                               (*key,observed.isoformat(),encoded))
                first.append({"close":bar["time"],"first_seen_at":saved[0] if saved else observed.isoformat()})
            result=scan_batch(BatchInput(candidates=[candidate]))[0]
            result["mode"]="RECEIPT_BOUND_UNIVERSE_RESEARCH_ONLY"
            known=instant(clock().isoformat())
            if not timedelta() <= known-observed <= timedelta(seconds=90) or known-close>timedelta(seconds=90):
                raise ValueError("Post-scan clock stale or backdated")
            timely=all(timedelta() <= instant(b["first_seen_at"])-instant(b["close"])
                       <= timedelta(seconds=90) for b in first[-3:])
            receipt={"receipt_id":identity,"version":VERSION,"symbol":candidate.symbol,
                "security_id":security_id,"universe_revision":revision,"candle_close":close.isoformat(),
                "observed_at":observed.isoformat(),"known_at":known.isoformat(),
                "reference_sha256":reference_sha256,"current_sha256":current_sha256,
                "candidate_sha256":digest(normalized),"input_fingerprint":fingerprint,
                "candles":current,"first_seen":first,"scanner_result":result,
                "receipt_status":"TIMELY_RESEARCH_EVIDENCE" if timely else "HELD_SETUP_FIRST_SEEN",
                "mode":"UNIVERSE_RECEIPT_RESEARCH_ONLY","timestamp_verified":False,
                "session_contract_verified":False,"reference_prices_verified":False,
                "breakout_receipts_verified":False,"forward_paper_ready":False,
                "execution_enabled":False}
            payload=encode(receipt)
            db.execute("INSERT INTO universe_receipt_signals VALUES ("+",".join([p]*3)+")",
                       (identity,payload,digest(receipt)))
            return {"status":"RECORDED","receipt":receipt}

    def read(self,receipt_id):
        if not re.fullmatch(r"[a-f0-9]{64}",receipt_id): raise ValueError("Receipt identity required")
        p="%s" if self.postgres else "?"
        with self.connection() as db:
            row=db.execute("SELECT payload,sha256 FROM universe_receipt_signals WHERE receipt_id="+p,
                           (receipt_id,)).fetchone()
            if not row: return None
            receipt=json.loads(row[0])
            if digest(receipt)!=row[1]: raise ValueError("Receipt integrity failure")
            cached=db.execute("SELECT payload,sha256 FROM universe_scan_reference_cache WHERE revision="+
                p+" AND security_id="+p,(receipt["universe_revision"],receipt["security_id"])).fetchone()
            if not cached or cached[1]!=receipt["reference_sha256"] or digest(json.loads(cached[0]))!=cached[1]:
                raise ValueError("Reference integrity failure")
            for bar,first in zip(receipt["candles"],receipt["first_seen"]):
                saved=db.execute("SELECT first_seen_at,payload FROM universe_receipt_candles WHERE symbol="+
                    p+" AND security_id="+p+" AND candle_close="+p,
                    (receipt["symbol"],receipt["security_id"],bar["time"])).fetchone()
                if not saved or saved[0]!=first["first_seen_at"] or saved[1]!=encode(bar):
                    raise ValueError("Candle/first-seen integrity failure")
        return receipt

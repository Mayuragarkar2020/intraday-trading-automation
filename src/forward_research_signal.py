"""Inactive receipt-bound research signal journal. Never execution clearance.

Current candles come exclusively from the recorder's committed observation.
Historical price inputs are preserved but remain unverified research inputs.
No runtime imports this module; no uploaded-diagnostics or order API uses it.
"""
import hashlib
import json
from datetime import datetime, timedelta

from src.candle_input import BatchInput, CandidateInput, CandleInput, scan_batch
from src.candle_session import ensure_ordered_session
from src.dhan_research_scanner import aggregate_15m
from src.forward_capture import IST
from src.forward_paper_ledger import encode, instant
from src.research_input_gate import prepare_research_inputs
from src.scan_store import ScanStore
from src.universe_store import validate_report

VERSION = "receipt-bound-research-v1"


def build_candidate(report, previous_sessions, reference_dates):
    """Derive all indicators' inputs; do not accept supplied EMA/15m values."""
    if len(previous_sessions) != 20 or len(reference_dates) != 20:
        raise ValueError("Exactly twenty reference sessions required")
    if any(len(day) != 72 for day in previous_sessions) or len(encode(previous_sessions)) > 2000000:
        raise ValueError("Bounded reference dataset required")
    previous = [[CandleInput.model_validate(b) for b in day] for day in previous_sessions]
    for expected, day in zip(reference_dates, previous):
        if len(day) != 72:
            raise ValueError("Reference session must match current 72-bar research assumption")
        ensure_ordered_session([b.time for b in day])
        if day[0].time[:10] != expected or day[0].time[11:16] != "09:20":
            raise ValueError("Reference dates/opening mismatch")
        # CandleInput alone does not validate OHLC relationships or finite volume types.
        for b in day:
            if (not all(x.is_finite() for x in (b.open,b.high,b.low,b.close)) or
                    b.high < max(b.open,b.close,b.low) or b.low > min(b.open,b.close)):
                raise ValueError("Invalid reference OHLC")
    current = [CandleInput.model_validate(b) for b in report["candles"]]
    if len(current) < 3:
        raise ValueError("Three completed current candles required")
    ensure_ordered_session([b.time for b in current])
    if current[0].time[11:16] != "09:20" or current[-1].time != report["expected_close"]:
        raise ValueError("Current session boundary mismatch")
    if any(b.time[:10] != report["session_date"] for b in current):
        raise ValueError("Cross-session capture")
    higher = [b for day in previous for b in aggregate_15m(day)]
    completed = len(current)//3*3
    higher.extend(aggregate_15m(current[:completed]))
    return CandidateInput(symbol="RELIANCE", completed_5m=current,
        previous_sessions=previous, completed_15m=higher[-150:],
        ema_warmup_closes=[b.close for day in previous for b in day][-200:])


class ForwardResearchSignalStore(ScanStore):
    def initialize(self):
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031012)")
            db.execute("""CREATE TABLE IF NOT EXISTS forward_research_signals (
                signal_id TEXT PRIMARY KEY, symbol TEXT NOT NULL, candle_close TEXT NOT NULL,
                payload TEXT NOT NULL, UNIQUE(symbol,candle_close))""")

    def record(self, observed_at, previous_sessions, *, clock=lambda: datetime.now(IST)):
        """Persist computed output and exact inputs after reading committed evidence.

        Caller may choose a stored observation, never supply current candles or
        scanner output. The clock is sampled after computation. The journal is
        research-only even if the computed scanner result says ARMED.
        """
        observed = instant(observed_at).isoformat()
        self.initialize()
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031013)")
            else:
                db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload FROM forward_research_observations WHERE symbol="+
                             p+" AND observed_at="+p, ("RELIANCE",observed)).fetchone()
            if not row:
                raise ValueError("Committed recorder observation required")
            report = json.loads(row[0])
            if (report["symbol"] != "RELIANCE" or report["security_id"] != "2885" or
                    report["observed_at"] != observed or report["status"] != "FRESH_OBSERVATION" or
                    report["missing_closes"] or report["execution_enabled"] is not False):
                raise ValueError("Fresh unmodified RELIANCE research capture required")
            digest = hashlib.sha256(encode(report["candles"]).encode()).hexdigest()
            if digest != report["source_sha256"]:
                raise ValueError("Capture source hash mismatch")
            first_seen = []
            for b in report["candles"]:
                saved = db.execute("SELECT first_observed_at,payload FROM forward_research_candles "
                                   "WHERE symbol="+p+" AND candle_close="+p,
                                   ("RELIANCE",b["time"])).fetchone()
                if not saved or saved[1] != encode(b) or instant(saved[0]) > instant(observed):
                    raise ValueError("Candle identity/first-seen mismatch")
                first_seen.append({"close": b["time"], "first_observed_at": saved[0]})
            # A reconnect/backfill is retained as evidence, never promoted to a timely signal.
            if report["late_first_observations"]:
                raise ValueError("Observation includes late first-seen candles")
            if any(not timedelta(0) <= instant(b["first_observed_at"]) - instant(b["close"])
                   <= timedelta(seconds=90) for b in first_seen[-3:]):
                raise ValueError("Setup candles were not first seen on time")
            revision = report["universe_revision"]
            universe = db.execute("SELECT target_date,asof_date,created_at,payload,evidence "
                                  "FROM universe_research_snapshots WHERE revision="+p,
                                  (revision,)).fetchone()
            if not universe or hashlib.sha256((universe[3]+"\n"+universe[4]).encode()).hexdigest() != revision:
                raise ValueError("Immutable universe revision required")
            snapshot = validate_report(json.loads(universe[3]))
            if ((snapshot["target_date"],snapshot["asof_date"]) != universe[:2] or
                    instant(universe[2]).date().isoformat() != report["session_date"] or
                    instant(universe[2]) > instant(observed)):
                raise ValueError("Universe publication/session mismatch")
            inputs = prepare_research_inputs(snapshot, instant(observed), "RELIANCE", "2885")
            if inputs["status"] != "RESEARCH_INPUTS_READY":
                raise ValueError("Research reference gate held")
            from src.daily_universe_refresh import reference_dates_for
            from src.run_forward_capture import CALENDAR
            calendar = json.loads(CALENDAR.read_text())
            target = report["session_date"]
            if (target not in calendar["sessions"] or
                    not calendar["earliest_target"] <= target <= calendar["latest_target"] or
                    inputs["reference_dates"] != reference_dates_for(target, calendar)):
                raise ValueError("Reviewed calendar/reference dates required")
            candidate = build_candidate(report, previous_sessions, inputs["reference_dates"])
            candidate_payload = candidate.model_dump(mode="json")
            input_hash = hashlib.sha256(encode(candidate_payload).encode()).hexdigest()
            identity = hashlib.sha256(encode([VERSION, revision, digest, input_hash]).encode()).hexdigest()
            old = db.execute("SELECT signal_id,payload FROM forward_research_signals WHERE symbol="+
                             p+" AND candle_close="+p, ("RELIANCE", report["expected_close"])).fetchone()
            if old:
                if old[0] != identity:
                    raise ValueError("Immutable signal input conflict")
                return {"status": "ALREADY_RECORDED", "signal": json.loads(old[1])}
            result = scan_batch(BatchInput(candidates=[candidate]))[0]
            result["mode"] = "RECEIPT_BOUND_RESEARCH_ONLY"
            known = clock()
            if known.tzinfo is None or known.utcoffset() is None:
                raise ValueError("Aware post-scan clock required")
            known = known.astimezone(IST)
            if (known.date().isoformat() != report["session_date"] or
                    not timedelta(0) <= known - instant(observed) <= timedelta(seconds=90) or
                    not timedelta(0) <= known - instant(report["expected_close"]) <= timedelta(seconds=90)):
                raise ValueError("Post-scan receipt clock is stale or backdated")
            signal = {"signal_id": identity, "version": VERSION, "symbol": "RELIANCE",
                      "security_id": "2885", "candle_close": report["expected_close"],
                      "observed_at": observed, "known_at": known.isoformat(),
                      "universe_revision": revision, "source_sha256": digest,
                      "candidate_sha256": input_hash, "candidate": candidate_payload,
                      "first_seen": first_seen, "scanner_result": result,
                      "mode": "RECEIPT_BOUND_RESEARCH_ONLY", "execution_enabled": False,
                      "forward_paper_ready": False, "reference_prices_verified": False,
                      "session_contract_verified": False}
            db.execute("INSERT INTO forward_research_signals VALUES ("+",".join([p]*4)+")",
                       (identity,"RELIANCE",report["expected_close"],encode(signal)))
            return {"status": "RECORDED", "signal": signal}


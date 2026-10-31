"""Append-only forward research observations. No orders or simulated fills.

The 15:15 cutoff is a conservative capture boundary for RELIANCE research,
not a verified per-instrument session classification or an exit policy.
"""
import hashlib
import json
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from src.dhan_candle_adapter import normalize_dhan_intraday
from src.scan_store import ScanStore

IST = ZoneInfo("Asia/Kolkata")
SYMBOL = "RELIANCE"
SECURITY_ID = "2885"


def prepare_capture(payload, now, universe_revision):
    if now.tzinfo is None or not isinstance(universe_revision, str) or not universe_revision:
        raise ValueError("Aware observation clock and universe revision required")
    local = now.astimezone(IST)
    if local.weekday() >= 5 or not time(9,20) <= local.time() <= time(15,25):
        raise ValueError("Outside conservative research capture window")
    close = local.replace(minute=local.minute // 5 * 5, second=0, microsecond=0)
    cutoff = local.replace(hour=15, minute=15, second=0, microsecond=0)
    expected_close = min(close, cutoff)
    bars = normalize_dhan_intraday(payload, as_of=local, timestamps_are_open=True)
    current = [b for b in bars if b.time[:10] == local.date().isoformat()
               and datetime.fromisoformat(b.time) <= expected_close]
    opening = local.replace(hour=9, minute=20, second=0, microsecond=0)
    expected = []
    cursor = opening
    while cursor <= expected_close:
        expected.append(cursor.isoformat())
        cursor += timedelta(minutes=5)
    received = {b.time for b in current}
    missing = [slot for slot in expected if slot not in received]
    latest = datetime.fromisoformat(current[-1].time) if current else None
    delay = (local - latest).total_seconds() if latest else None
    status = "NO_CURRENT_CANDLES" if not current else "INCOMPLETE_SESSION" if missing else (
        "STALE" if delay > 90 else "FRESH_OBSERVATION")
    candles = [{"time": b.time, "open": format(b.open.normalize(), "f"),
                "high": format(b.high.normalize(), "f"),
                "low": format(b.low.normalize(), "f"),
                "close": format(b.close.normalize(), "f"), "volume": b.volume}
               for b in current]
    canonical = json.dumps(candles, sort_keys=True, separators=(",", ":"))
    return {"session_date": local.date().isoformat(), "symbol": SYMBOL,
            "security_id": SECURITY_ID, "expected_close": expected_close.isoformat(),
            "observed_at": local.isoformat(), "universe_revision": universe_revision,
            "status": status, "missing_closes": missing, "latest_delay_seconds": delay,
            "candles": candles, "source_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "timestamp_basis": "OPEN_ASSUMPTION_SUPPORTED_BY_ONE_RELIANCE_CHART_SAMPLE",
            "session_boundary": "CONSERVATIVE_15_15_RESEARCH_CUTOFF_NOT_DAILY_CAS_VERIFICATION",
            "forward_paper_ready": False, "execution_enabled": False}


class ForwardCaptureStore(ScanStore):
    def initialize(self):
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031008)")
            db.execute("""CREATE TABLE IF NOT EXISTS forward_research_candles (
                symbol TEXT NOT NULL, candle_close TEXT NOT NULL,
                first_observed_at TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(symbol,candle_close))""")
            db.execute("""CREATE TABLE IF NOT EXISTS forward_research_observations (
                symbol TEXT NOT NULL, observed_at TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(symbol,observed_at))""")

    def save(self, report):
        """Serialize writers; any changed candle rolls the entire observation back."""
        self.initialize()
        placeholder = "%s" if self.postgres else "?"
        with self.connection() as db:
            if self.postgres:
                db.execute("SELECT pg_advisory_xact_lock(73031009)")
            else:
                db.execute("BEGIN IMMEDIATE")
            inserted = 0
            late = []
            for candle in report["candles"]:
                values = (report["symbol"], candle["time"])
                query = "SELECT payload FROM forward_research_candles WHERE symbol="+placeholder+" AND candle_close="+placeholder
                old = db.execute(query, values).fetchone()
                encoded = json.dumps(candle, sort_keys=True, separators=(",", ":"))
                if old:
                    if old[0] != encoded:
                        raise ValueError("Historical candle revision detected")
                    continue
                delay = (datetime.fromisoformat(report["observed_at"]) - datetime.fromisoformat(candle["time"])).total_seconds()
                if delay > 90:
                    late.append(candle["time"])
                db.execute("INSERT INTO forward_research_candles VALUES ("+",".join([placeholder]*4)+")",
                           (*values, report["observed_at"], encoded))
                inserted += 1
            saved = {**report, "new_candles": inserted,
                     "late_first_observations": late,
                     "backfilled_candles_are_trade_events": False}
            encoded_report = json.dumps(saved, sort_keys=True)
            key = (report["symbol"], report["observed_at"])
            old = db.execute("SELECT payload FROM forward_research_observations WHERE symbol="+placeholder+" AND observed_at="+placeholder, key).fetchone()
            if old:
                # Same clock is idempotent only for the same source/reference observation.
                original = json.loads(old[0])
                if any(original[k] != report[k] for k in report):
                    raise ValueError("Observation identity conflict")
                return {"status": "ALREADY_CAPTURED", "report": original}
            db.execute("INSERT INTO forward_research_observations VALUES ("+",".join([placeholder]*3)+")",
                       (*key, encoded_report))
            return {"status": "CAPTURED", "report": saved}

    def latest(self):
        with self.connection() as db:
            row = db.execute("SELECT payload FROM forward_research_observations ORDER BY observed_at DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else None

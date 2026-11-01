"""Inactive full-universe research scanner. No orders or scheduler wiring.

Reuse the existing daily universe and setup detector. Fetch twenty-session
reference prices once per universe/instrument, then current candles per cycle.
Each stock has an explicit scanned/excluded/held outcome. No chart screenshots
are a daily per-stock prerequisite. Data/session assumptions remain research-only.
"""
from collections import Counter
from datetime import datetime, time, timedelta
import hashlib
import json
import re
import sqlite3
import time as runtime
from zoneinfo import ZoneInfo

import httpx

from src.candle_input import BatchInput, CandidateInput, scan_batch
from src.candle_session import ensure_ordered_session
from src.daily_universe_refresh import reference_dates_for
from src.dhan_candle_adapter import normalize_dhan_intraday
from src.dhan_history_client import fetch_intraday
from src.dhan_research_scanner import aggregate_15m
from src.research_input_gate import prepare_research_inputs
from src.run_forward_capture import CALENDAR
from src.scan_store import ScanStore

IST = ZoneInfo("Asia/Kolkata")
VERSION = "universe-research-scan-v1"
FIELDS = ("timestamp","open","high","low","close","volume")


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


class UniverseScanStore(ScanStore):
    def initialize(self):
        with self.connection() as db:
            if self.postgres: db.execute("SELECT pg_advisory_xact_lock(73031016)")
            db.execute("""CREATE TABLE IF NOT EXISTS universe_scan_reference_cache (
                revision TEXT NOT NULL, security_id TEXT NOT NULL,
                payload TEXT NOT NULL, sha256 TEXT NOT NULL,
                PRIMARY KEY(revision,security_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS universe_scan_cycles (
                cycle_id TEXT PRIMARY KEY, candle_close TEXT NOT NULL,
                mode TEXT NOT NULL, payload TEXT NOT NULL)""")

    def reference(self,revision,security_id):
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            row = db.execute("SELECT payload,sha256 FROM universe_scan_reference_cache "
                "WHERE revision="+p+" AND security_id="+p,(revision,security_id)).fetchone()
        if not row: return None
        payload = json.loads(row[0])
        if digest(payload) != row[1]: raise ValueError("Reference cache integrity failure")
        return payload

    def save_reference(self,revision,security_id,payload):
        p = "%s" if self.postgres else "?"
        values = (revision,security_id,encoded(payload),digest(payload))
        with self.connection() as db:
            db.execute("INSERT INTO universe_scan_reference_cache VALUES ("+",".join([p]*4)+
                ") ON CONFLICT DO NOTHING",values)
        old = self.reference(revision,security_id)
        if old != payload: raise ValueError("Immutable reference cache conflict")

    def cycle(self,cycle_id):
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            row = db.execute("SELECT payload FROM universe_scan_cycles WHERE cycle_id="+p,(cycle_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save_cycle(self,report):
        p = "%s" if self.postgres else "?"
        with self.connection() as db:
            cursor = db.execute("INSERT INTO universe_scan_cycles VALUES ("+",".join([p]*4)+
                ") ON CONFLICT DO NOTHING",(report["cycle_id"],report["candle_close"],report["mode"],encoded(report)))
            inserted = cursor.rowcount == 1
        return {"status":"SCANNED" if inserted else "ALREADY_SCANNED",
                "report":self.cycle(report["cycle_id"]),"execution_enabled":False}

    def latest_scan(self):
        """Read-only: absent new tables fall back; real database errors propagate."""
        try:
            with self.connection() as db:
                row = db.execute("SELECT payload FROM universe_scan_cycles "
                    "WHERE mode='FULL_UNIVERSE_RESEARCH_ONLY' ORDER BY candle_close DESC,cycle_id DESC LIMIT 1").fetchone()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc): return None
            raise
        except Exception as exc:
            if getattr(exc,"sqlstate",None)=="42P01": return None
            raise
        return json.loads(row[0]) if row else None


def cockpit_snapshot(report):
    if (report.get("mode")!="FULL_UNIVERSE_RESEARCH_ONLY" or report.get("execution_enabled") is not False
            or report.get("forward_paper_ready") is not False):
        raise ValueError("Research-only scan required")
    setups = [{"symbol":r["symbol"],"status":r.get("setup_status") if r["status"]=="SCANNED" else "HOLD",
        "reason":r["reason"],"entry":r.get("entry"),"stop":r.get("stop"),"execution_enabled":False}
        for r in report["rows"] if r["selected"]]
    return {"status":"AVAILABLE","source":"PERSISTED_UNIVERSE_SCAN","live":False,"execution_enabled":False,
        "snapshot":{"candle_close":report["candle_close"],"setups":setups},
        "coverage":{"selected":report["selected_count"],"scanned":report["summary"].get("SCANNED",0),
                    "complete":report["coverage_complete"]}}


def prepare_history(raw,now,dates):
    bars = normalize_dhan_intraday(raw,as_of=now,timestamps_are_open=True)
    groups = {}
    for bar in bars:
        day = bar.time[:10]
        if dates[0] <= day < now.astimezone(IST).date().isoformat():
            groups.setdefault(day,[]).append(bar)
    if set(groups) != set(dates): raise ValueError("Exact reference dates required")
    previous = [groups[day] for day in dates]
    for day in previous:
        ensure_ordered_session([b.time for b in day])
        # Both regular shapes are research assumptions, never dated CAS certification.
        if len(day) not in (72,75) or day[0].time[11:16] != "09:20":
            raise ValueError("Incomplete reference session")
    return previous


def candidate_from(symbol,previous,current_raw,received,close):
    bars = normalize_dhan_intraday(current_raw,as_of=received,timestamps_are_open=True)
    today = close.date().isoformat()
    current = [b for b in bars if b.time[:10] == today and datetime.fromisoformat(b.time) <= close]
    if not current or current[-1].time != close.isoformat():
        raise ValueError("Latest completed candle missing")
    ensure_ordered_session([b.time for b in current])
    if current[0].time[11:16] != "09:20": raise ValueError("Opening candles missing")
    if not timedelta(0) <= received-close <= timedelta(seconds=90):
        raise ValueError("Cycle candle stale at receipt")
    higher = [b for day in previous for b in aggregate_15m(day)]
    higher.extend(aggregate_15m(current[:len(current)//3*3]))
    return CandidateInput(symbol=symbol,completed_5m=current,previous_sessions=previous,
        completed_15m=higher[-150:],ema_warmup_closes=[b.close for day in previous for b in day][-200:])


def run_universe_scan(now,universe_store,store,token,*,fetch=fetch_intraday,
                      clock=lambda:datetime.now(IST),monotonic=runtime.monotonic,
                      sleep=runtime.sleep,budget_seconds=180,_warm_only=False,receipt_store=None):
    """One bounded sequential scan. Not called by the production cron.

    Per-worker spacing is 0.3s; activation must coordinate other consumers of
    the same broker credentials. Authentication/rate-limit failures stop the
    remaining requests. Reference/cache failures never become scan successes.
    """
    def hold(reason): return {"status":reason,"execution_enabled":False,"forward_paper_ready":False}
    if now.tzinfo is None or now.utcoffset() is None: raise ValueError("Aware clock required")
    if type(budget_seconds) not in (int,float) or not 1 <= budget_seconds <= 240:
        raise ValueError("Bounded cycle budget required")
    local = now.astimezone(IST)
    target = local.date().isoformat()
    calendar = json.loads(CALENDAR.read_text())
    if target not in calendar["sessions"] or not calendar["earliest_target"] <= target <= calendar["latest_target"]:
        return hold("UNREVIEWED_SESSION")
    if _warm_only:
        if not time(8,30) <= local.time() < time(9,40): return hold("OUTSIDE_WARMUP_WINDOW")
    elif not time(9,45) <= local.time() <= time(11,30): return hold("OUTSIDE_SETUP_WINDOW")
    if not isinstance(token,str) or not token: return hold("DHAN_TOKEN_NOT_CONFIGURED")
    published = universe_store.latest(target)
    if (not published or not re.fullmatch(r"[a-f0-9]{64}",published.get("revision","")) or
            datetime.fromisoformat(published["created_at"]).tzinfo is None or
            datetime.fromisoformat(published["created_at"]).astimezone(IST).date().isoformat() != target or
            datetime.fromisoformat(published["created_at"]) > now):
        return hold("SAME_DAY_UNIVERSE_REQUIRED")
    report = published["snapshot"]
    rows = report.get("candidates",[])
    if not isinstance(rows,list) or not 1 <= len(rows) <= 2000:
        return hold("INVALID_UNIVERSE_SIZE")
    close = local.replace(minute=local.minute//5*5,second=0,microsecond=0)
    cycle_id = digest([VERSION,"WARMUP" if _warm_only else "SCAN",published["revision"],close.isoformat()])
    store.initialize()
    old = store.cycle(cycle_id)
    if old: return {"status":"ALREADY_SCANNED","report":old,"execution_enabled":False}
    symbols = Counter(row.get("symbol") for row in rows)
    ids = Counter(row.get("dhan_security_id") for row in rows)
    start = monotonic()
    last_request = None
    requests = 0
    stopped = None
    outcomes = []
    def request(sid,from_date,to_date):
        nonlocal requests,last_request
        if monotonic()-start >= budget_seconds: raise TimeoutError("Cycle budget")
        if last_request is not None:
            delay = 0.3-(monotonic()-last_request)
            if delay > 0: sleep(delay)
        if monotonic()-start >= budget_seconds: raise TimeoutError("Cycle budget")
        last_request = monotonic()
        requests += 1
        return fetch(token,sid,5,from_date,to_date)
    # Snapshot liquidity ordering determines coverage if a slow source exhausts the budget.
    for row in rows:
        symbol,sid = row.get("symbol"),row.get("dhan_security_id")
        result = {"symbol":symbol,"security_id":sid,"status":"HOLD","selected":False,"execution_enabled":False}
        outcomes.append(result)
        if row.get("reference_price_band") in {"2","5",2,5}:
            result.update(status="EXCLUDED",reason="LOW_PRICE_BAND"); continue
        if row.get("reference_price_band") not in {"10","20","No Band",10,20}:
            result["reason"] = "UNKNOWN_PRICE_BAND"; continue
        if str(row.get("reference_review_status","")).startswith("EXCLUDED"):
            result.update(status="EXCLUDED",reason=row["reference_review_status"]); continue
        if symbols[symbol] != 1 or ids[sid] != 1:
            result["reason"] = "DUPLICATE_INSTRUMENT_IDENTITY"; continue
        if not isinstance(sid,str) or not re.fullmatch(r"[0-9]{1,12}",sid):
            result["reason"] = "INVALID_SECURITY_ID"; continue
        gate = prepare_research_inputs(report,local,symbol,sid)
        if gate["status"] != "RESEARCH_INPUTS_READY":
            result["reason"] = gate["status"]; continue
        if gate["reference_dates"] != reference_dates_for(target,calendar):
            result["reason"] = "REFERENCE_CALENDAR_MISMATCH"; continue
        result["selected"] = True
        if stopped:
            result["reason"] = stopped; continue
        try:
            cached = store.reference(published["revision"],sid)
            if cached is None:
                history_raw = request(sid,(local-timedelta(days=50)).strftime("%Y-%m-%d 09:15:00"),
                                      local.strftime("%Y-%m-%d 09:15:00"))
                prepare_history(history_raw,local,gate["reference_dates"])
                # Retain only historical records, never cache current-session prices.
                keep = [i for i,t in enumerate(history_raw["timestamp"])
                        if datetime.fromtimestamp(int(t),IST).date().isoformat() in gate["reference_dates"]]
                cached = {k:[history_raw[k][i] for i in keep] for k in FIELDS}
                store.save_reference(published["revision"],sid,cached)
            previous = prepare_history(cached,local,gate["reference_dates"])
            if _warm_only:
                result.update(status="REFERENCE_READY",reference_sha256=digest(cached))
                continue
            raw = request(sid,(local-timedelta(days=1)).strftime("%Y-%m-%d 09:15:00"),
                          (local+timedelta(days=1)).strftime("%Y-%m-%d 09:15:00"))
            received = clock()
            if received.tzinfo is None or received.utcoffset() is None or received < now:
                raise ValueError("Invalid receipt clock")
            received = received.astimezone(IST)
            candidate = candidate_from(symbol,previous,raw,received,close)
            if receipt_store is None:
                scan = scan_batch(BatchInput(candidates=[candidate]))[0]
            else:
                receipt = receipt_store.record(published["revision"],sid,candidate,
                    digest(cached),digest(raw),received.isoformat(),clock=clock)["receipt"]
                scan = receipt["scanner_result"]
                result.update(receipt_id=receipt["receipt_id"],known_at=receipt["known_at"],
                              receipt_status=receipt["receipt_status"])
            result.update(status="HOLD" if scan["status"]=="BLOCK" else "SCANNED",
                setup_status=scan["status"],reason=scan["reason"],
                entry=scan["entry"],stop=scan["stop"],observed_at=received.isoformat(),
                candle_close=close.isoformat(),reference_sha256=digest(cached),current_sha256=digest(raw))
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            stopped = "BROKER_AUTH_HOLD" if code in (401,403) else "BROKER_RATE_LIMIT_HOLD" if code==429 else None
            result["reason"] = stopped or "BROKER_FETCH_FAILED"
        except TimeoutError:
            stopped = "CYCLE_BUDGET_EXHAUSTED"
            result["reason"] = stopped
        except (ValueError,TypeError,KeyError,OverflowError,httpx.HTTPError):
            result["reason"] = "INVALID_OR_UNAVAILABLE_CANDLE_DATA"
    summary = dict(Counter(row["status"] for row in outcomes))
    selected = sum(row["selected"] for row in outcomes)
    return store.save_cycle({"cycle_id":cycle_id,"version":VERSION,"universe_revision":published["revision"],
        "session_date":target,"candle_close":close.isoformat(),
        "mode":"REFERENCE_WARMUP_RESEARCH_ONLY" if _warm_only else "FULL_UNIVERSE_RESEARCH_ONLY",
        "rows":outcomes,"summary":summary,"broker_requests":requests,
        "selected_count":selected,"coverage_complete":selected>0 and selected==summary.get("REFERENCE_READY" if _warm_only else "SCANNED",0),
        "receipt_evidence_enabled":receipt_store is not None,
        "receipt_summary":dict(Counter(r.get("receipt_status","NO_RECEIPT") for r in outcomes if r["selected"])),
        "timestamp_verified":False,"session_classification_verified":False,
        "execution_enabled":False,"forward_paper_ready":False})


def warm_universe_references(now,universe_store,store,token,**kwargs):
    """Warm/retry only missing reference prices before the entry window."""
    return run_universe_scan(now,universe_store,store,token,_warm_only=True,**kwargs)

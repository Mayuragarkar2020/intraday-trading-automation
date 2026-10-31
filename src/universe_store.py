"""Append-only research universes shared by scheduler and cockpit."""
import hashlib
import json
from datetime import date, datetime, timezone
from src.scan_store import ScanStore
from src.nse_eligibility_audit import audit_eligibility

def validate_report(report):
    if (not isinstance(report, dict) or report.get("mode") != "LIQUIDITY_RESEARCH_ONLY"
            or report.get("execution_enabled") is not False
            or report.get("tradable_count") != 0
            or report.get("restrictions_verified") is not False
            or report.get("calendar_completeness_verified") is not False):
        raise ValueError("Unexpected research universe mode")
    try:
        target = date.fromisoformat(report["target_date"])
        asof = date.fromisoformat(report["asof_date"])
        if target.isoformat() != report["target_date"] or asof.isoformat() != report["asof_date"] or asof >= target:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ValueError("Invalid universe dates") from None
    return report

class UniverseStore:
    def __init__(self, database_url):
        self.backend = ScanStore(database_url)

    def initialize(self):
        with self.backend.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS universe_research_snapshots(
                revision TEXT PRIMARY KEY, target_date TEXT NOT NULL, asof_date TEXT NOT NULL,
                created_at TEXT NOT NULL, payload TEXT NOT NULL, evidence TEXT NOT NULL)""")
            db.execute("""CREATE INDEX IF NOT EXISTS universe_research_target_idx
                ON universe_research_snapshots(target_date, created_at)""")

    def publish(self, report, evidence, *, now=None):
        validate_report(report)
        if not isinstance(evidence, dict) or "nse" not in evidence:
            raise ValueError("NSE evidence required")
        if audit_eligibility(report, evidence["nse"]) != report:
            raise ValueError("Universe does not reproduce from its evidence")
        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("Timezone-aware publication time required")
        payload = json.dumps(report, sort_keys=True, separators=(",", ":"))
        proof = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
        revision = hashlib.sha256((payload + "\n" + proof).encode()).hexdigest()
        created = now.astimezone(timezone.utc).isoformat()
        with self.backend.connection() as db:
            statement = (
                "INSERT INTO universe_research_snapshots VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING"
                if self.backend.postgres else
                "INSERT OR IGNORE INTO universe_research_snapshots VALUES (?,?,?,?,?,?)")
            cursor = db.execute(statement, (revision, report["target_date"], report["asof_date"],
                                            created, payload, proof))
        return {"revision": revision, "inserted": cursor.rowcount == 1}

    def latest(self, target_date=None):
        query = "SELECT revision,target_date,asof_date,created_at,payload,evidence FROM universe_research_snapshots"
        parameters = ()
        if target_date is not None:
            if date.fromisoformat(target_date).isoformat() != target_date:
                raise ValueError("Canonical target date required")
            query += " WHERE target_date=" + ("%s" if self.backend.postgres else "?")
            parameters = (target_date,)
        query += " ORDER BY target_date DESC,created_at DESC,revision DESC LIMIT 1"
        with self.backend.connection() as db:
            row = db.execute(query, parameters).fetchone()
        if not row:
            return None
        digest = hashlib.sha256((row[4] + "\n" + row[5]).encode()).hexdigest()
        if digest != row[0]:
            raise ValueError("Universe content hash mismatch")
        report = validate_report(json.loads(row[4]))
        if (report["target_date"], report["asof_date"]) != (row[1], row[2]):
            raise ValueError("Universe index dates mismatch")
        return {"revision": row[0], "created_at": row[3], "snapshot": report}

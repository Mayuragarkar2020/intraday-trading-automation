"""Append-only, content-addressed paper runs in the existing research database."""
import json
import sqlite3
from datetime import datetime, timezone
from src.scan_store import ScanStore

class PaperStore(ScanStore):
    def initialize(self):
        with self.connection() as db:
            if self.postgres:db.execute("SELECT pg_advisory_xact_lock(73031006)")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_replay_runs (
                run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,
                input_payload TEXT NOT NULL, result_payload TEXT NOT NULL)""")

    def save(self, request, result):
        self.initialize()
        with self.connection() as db:
            values=(result["run_id"],datetime.now(timezone.utc).isoformat(),
                    request.model_dump_json(),json.dumps(result,sort_keys=True))
            sql="INSERT INTO paper_replay_runs VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING" if self.postgres else "INSERT OR IGNORE INTO paper_replay_runs VALUES (?,?,?,?)"
            return db.execute(sql,values).rowcount==1

    def _read(self, query, values=()):
        try:
            with self.connection() as db:
                return db.execute(query,values).fetchall()
        except sqlite3.OperationalError as error:
            if "no such table" in str(error):return []
            raise
        except Exception as error:
            # PostgreSQL undefined-table only. Connectivity and other errors remain errors.
            if getattr(error,"sqlstate",None)=="42P01":return []
            raise

    def recent(self):
        rows=self._read("SELECT run_id,created_at,result_payload FROM paper_replay_runs ORDER BY created_at DESC,run_id DESC LIMIT 20")
        return [{"run_id":rid,"created_at":at,"label":(r:=json.loads(payload))["label"],
                 "source":r["source"],"summary":r["summary"]} for rid,at,payload in rows]

    def get(self, run_id):
        rows=self._read("SELECT input_payload,result_payload FROM paper_replay_runs WHERE run_id="+("%s" if self.postgres else "?"),(run_id,))
        return {"input":json.loads(rows[0][0]),"result":json.loads(rows[0][1])} if rows else None

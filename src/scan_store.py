"""Durable, read-only scan snapshot store. PostgreSQL for cloud, SQLite for tests.

No broker order routes. Snapshot and checkpoint are committed atomically.
"""
import json
import sqlite3
from contextlib import contextmanager

class ScanStore:
    def __init__(self,database_url):
        self.database_url=database_url
        self.postgres=database_url.startswith(("postgresql://","postgres://"))
        if not self.postgres and not database_url.startswith("sqlite:///"):
            raise ValueError("Use PostgreSQL URL or sqlite:/// path")

    @contextmanager
    def connection(self):
        if self.postgres:
            import psycopg
            with psycopg.connect(self.database_url) as db:
                yield db
        else:
            with sqlite3.connect(self.database_url[len("sqlite:///"):],timeout=5) as db:
                yield db

    def initialize(self):
        with self.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scan_snapshots(
                candle_close TEXT PRIMARY KEY, payload TEXT NOT NULL)""")

    def commit_scan(self,candle_close,rows):
        """Returns False for duplicate; never overwrites an existing scan."""
        payload=json.dumps(rows,sort_keys=True)
        with self.connection() as db:
            cursor=db.execute(
                "INSERT INTO scan_snapshots(candle_close,payload) VALUES (%s,%s) ON CONFLICT DO NOTHING"
                if self.postgres else
                "INSERT OR IGNORE INTO scan_snapshots(candle_close,payload) VALUES (?,?)",
                (candle_close,payload))
            return cursor.rowcount==1

    def latest(self):
        with self.connection() as db:
            row=db.execute("SELECT candle_close,payload FROM scan_snapshots ORDER BY candle_close DESC LIMIT 1").fetchone()
        if not row:return None
        return {"candle_close":row[0],"setups":json.loads(row[1])}

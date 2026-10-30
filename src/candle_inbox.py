"""Shared, durable, validated candle batch inbox for independent cloud workers.

Publishing is allowed only for complete Pydantic-validated snapshots.
No Dhan credentials, quotes, or order routes here.
"""
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from src.candle_input import BatchInput
from src.candle_session import ensure_ordered_session

class CandleInbox:
    def __init__(self, database_url):
        self.database_url=database_url
        self.postgres=database_url.startswith(("postgresql://","postgres://"))
        if not self.postgres and not database_url.startswith("sqlite:///"):
            raise ValueError("Expected Postgres or SQLite URI")

    @contextmanager
    def connection(self):
        if self.postgres:
            import psycopg
            with psycopg.connect(self.database_url) as db:yield db
        else:
            with sqlite3.connect(self.database_url[10:],timeout=5) as db:yield db

    def initialize(self):
        with self.connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS candle_batches(
                candle_close TEXT PRIMARY KEY,
                digest TEXT NOT NULL,
                payload TEXT NOT NULL)""")

    def publish(self,batch:BatchInput):
        closes={ensure_ordered_session([c.time for c in row.completed_5m]) and row.completed_5m[-1].time
                for row in batch.candidates}
        if len(closes)!=1:raise ValueError("Candidate closes do not match")
        close=closes.pop()
        symbols=[row.symbol for row in batch.candidates]
        if len(symbols)!=len(set(symbols)):raise ValueError("Duplicate symbol")
        payload=batch.model_dump_json()
        digest=hashlib.sha256(payload.encode()).hexdigest()
        sql=("INSERT INTO candle_batches (candle_close,digest,payload) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING"
             if self.postgres else
             "INSERT OR IGNORE INTO candle_batches (candle_close,digest,payload) VALUES (?,?,?)")
        with self.connection() as db:
            inserted=db.execute(sql,(close,digest,payload)).rowcount==1
        return {"status":"PUBLISHED" if inserted else "ALREADY_EXISTS","candle_close":close}

    def fetch(self,candle_close):
        param="%s" if self.postgres else "?"
        with self.connection() as db:
            row=db.execute("SELECT digest,payload FROM candle_batches WHERE candle_close="+param,
                           (candle_close,)).fetchone()
        if not row:return None
        digest,payload=row
        if hashlib.sha256(payload.encode()).hexdigest()!=digest:
            raise ValueError("Stored candle data checksum mismatch")
        return BatchInput.model_validate_json(payload)

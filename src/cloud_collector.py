"""Five-minute cloud collector orchestration. No broker or order execution.

A persistent SQLite checkpoint prevents repeating a completed scan after
restarts. A single worker must own this file; cloud deployments should use
Postgres instead of ephemeral filesystem storage.
"""
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from src.candle_session import IST, parse_close
from src.candle_input import BatchInput, scan_batch

def eligible_close(now:datetime,settle_seconds:int=10):
    if now.tzinfo is None:raise ValueError("Timezone-aware clock required")
    local=now.astimezone(IST)-timedelta(seconds=settle_seconds)
    minute=local.minute-(local.minute%5)
    boundary=local.replace(minute=minute,second=0,microsecond=0)
    try:return parse_close(boundary.isoformat())
    except ValueError:return None

class CheckpointCollector:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS scan_checkpoint (session_close TEXT PRIMARY KEY, result_count INTEGER NOT NULL)")
    def scan(self,now:datetime,batch:BatchInput):
        close=eligible_close(now)
        if close is None:return {"status":"OUTSIDE_SESSION","execution_enabled":False}
        key=close.isoformat()
        with sqlite3.connect(self.path,timeout=5,isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM scan_checkpoint WHERE session_close=?",(key,)).fetchone():
                db.execute("COMMIT")
                return {"status":"ALREADY_SCANNED","candle_close":key,"execution_enabled":False}
            if any(parse_close(c.completed_5m[-1].time)!=close for c in batch.candidates):
                db.execute("ROLLBACK")
                return {"status":"WAIT_FOR_COMPLETE_CANDLES","candle_close":key,"execution_enabled":False}
            result=scan_batch(batch)
            db.execute("INSERT INTO scan_checkpoint VALUES (?,?)",(key,len(result)))
            db.execute("COMMIT")
            return {"status":"SCANNED","candle_close":key,"setups":result,"execution_enabled":False}

class PersistentScanCollector:
    """One atomic scan per candle close, shared across cloud workers via ScanStore."""
    def __init__(self,store):
        self.store=store
        self.store.initialize()

    def scan(self,now:datetime,batch:BatchInput):
        close=eligible_close(now)
        if close is None:return {"status":"OUTSIDE_SESSION","execution_enabled":False}
        key=close.isoformat()
        if any(parse_close(x.completed_5m[-1].time)!=close for x in batch.candidates):
            return {"status":"WAIT_FOR_COMPLETE_CANDLES","candle_close":key,"execution_enabled":False}
        rows=scan_batch(batch)
        inserted=self.store.commit_scan(key,rows)
        return {"status":"SCANNED" if inserted else "ALREADY_SCANNED",
                "candle_close":key,"execution_enabled":False,
                "setups":rows if inserted else []}

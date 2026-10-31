import copy
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
import pytest
from src.universe_store import UniverseStore
from src.research_snapshot import load_research_snapshot

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture
def sample():
    report=json.loads((ROOT/"research/2026-10-30/universe.json").read_text(encoding="utf-8"))
    nse=json.loads((ROOT/"research/2026-10-30/nse-eligibility-evidence.json").read_text(encoding="utf-8"))
    report["test_nonce"]=uuid.uuid4().hex
    return report, {"nse":nse}

@pytest.fixture(params=["sqlite","postgres"])
def store(request,tmp_path):
    if request.param=="postgres":
        url=os.getenv("TEST_UNIVERSE_DATABASE_URL")
        if not url:
            pytest.skip("Ephemeral PostgreSQL CI database not configured")
        parsed=urlparse(url)
        if (parsed.hostname not in {"localhost","127.0.0.1"} or parsed.username!="research_test"
                or parsed.path!="/research_test_store"):
            raise ValueError("Only the dedicated local CI database may be used")
    else:
        url="sqlite:///"+str(tmp_path/"universe.db")
    result=UniverseStore(url)
    result.initialize()
    if request.param=="postgres":
        # This database is an isolated CI service, never the Render database.
        with result.backend.connection() as db:
            db.execute("DELETE FROM universe_research_snapshots")
    return result

def test_atomic_publication_and_hash_round_trip(store,sample):
    report,evidence=sample
    saved=store.publish(report,evidence)
    current=store.latest(report["target_date"])
    assert saved["inserted"] is True
    assert current["revision"]==saved["revision"]
    assert current["snapshot"]==report
    assert store.publish(report,evidence)["inserted"] is False
    assert store.latest("2026-11-03") is None

def test_later_correction_is_append_only(store,sample):
    report,evidence=sample
    first=store.publish(report,evidence,now=datetime(2026,10,31,tzinfo=timezone.utc))
    corrected=copy.deepcopy(report)
    corrected["correction_note"]="Reviewed reference observation"
    second=store.publish(corrected,evidence,now=datetime(2026,10,31,tzinfo=timezone.utc)+timedelta(minutes=1))
    assert second["revision"]!=first["revision"]
    assert store.latest(report["target_date"])["revision"]==second["revision"]
    with store.backend.connection() as db:
        assert db.execute("SELECT count(*) FROM universe_research_snapshots").fetchone()[0]==2

def test_unverified_evidence_cannot_publish(store,sample):
    report,evidence=sample
    evidence["nse"]["gsm"]["payload"][0]["symbol"]="ALTERED"
    with pytest.raises(ValueError,match="hash"):
        store.publish(report,evidence)
    assert store.latest() is None

def test_unsafe_execution_mode_rejected(store,sample):
    report,evidence=sample
    report["execution_enabled"]=True
    with pytest.raises(ValueError,match="mode"):
        store.publish(report,evidence)
    assert store.latest() is None

def test_content_corruption_detected(store,sample):
    report,evidence=sample
    store.publish(report,evidence)
    with store.backend.connection() as db:
        db.execute("UPDATE universe_research_snapshots SET payload='{}'")
    with pytest.raises(ValueError,match="hash mismatch"):
        store.latest()

def test_dashboard_loads_shared_snapshot_without_enabling_execution(store,sample,monkeypatch):
    report,evidence=sample
    store.publish(report,evidence)
    monkeypatch.setenv("SCAN_DATABASE_URL",store.backend.database_url)
    result=load_research_snapshot()
    assert result["source"]=="PERSISTED_DAILY_RESEARCH_UNIVERSE"
    assert result["snapshot"]==report
    assert result["execution_enabled"] is False

def test_dashboard_read_does_not_initialize_schema(tmp_path,monkeypatch):
    import sqlite3
    path=tmp_path/"uninitialized.db"
    monkeypatch.setenv("SCAN_DATABASE_URL","sqlite:///"+str(path))
    result=load_research_snapshot()
    assert result["source"]=="DATED_NSE_RESEARCH_SNAPSHOT"
    assert "unavailable" in result["availability"]
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]==0

from fastapi.testclient import TestClient
import pytest

import src.cloud_app as app_module
from src.universe_scanner import UniverseScanStore,cockpit_snapshot


def snapshot():
    return {"mode":"FULL_UNIVERSE_RESEARCH_ONLY","execution_enabled":False,"forward_paper_ready":False,
        "candle_close":"2026-11-02T09:45:00+05:30","selected_count":2,"coverage_complete":False,
        "summary":{"SCANNED":1,"HOLD":1,"EXCLUDED":1},"rows":[
            {"symbol":"STOCK0","selected":True,"status":"SCANNED","setup_status":"ARMED","reason":"WAIT_FOR_NEXT_CANDLE_BREAKOUT","entry":"101.05","stop":"98.95"},
            {"symbol":"STOCK1","selected":True,"status":"HOLD","reason":"INVALID_OR_UNAVAILABLE_CANDLE_DATA"},
            {"symbol":"LOWBAND","selected":False,"status":"EXCLUDED","reason":"LOW_PRICE_BAND"}]}


def test_selected_hold_remains_visible_but_exclusions_do_not_become_scan_rows():
    result=cockpit_snapshot(snapshot())
    assert len(result["snapshot"]["setups"])==2
    assert result["snapshot"]["setups"][1]["status"]=="HOLD"
    assert result["coverage"]=={"selected":2,"scanned":1,"complete":False}
    assert not result["live"] and not result["execution_enabled"]


def test_snapshot_cannot_be_promoted_to_execution():
    report=snapshot();report["execution_enabled"]=True
    with pytest.raises(ValueError): cockpit_snapshot(report)


def test_new_tables_are_not_created_by_dashboard_read(tmp_path):
    backend=UniverseScanStore("sqlite:///"+str(tmp_path/"read.db"))
    assert backend.latest_scan() is None
    with backend.connection() as db:
        assert db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()==[]


def test_api_returns_full_pool_with_auth_and_safe_store_failure(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","fixture-access")
    monkeypatch.setenv("SCAN_DATABASE_URL","sqlite:///unused-fixture")
    monkeypatch.setattr(UniverseScanStore,"latest_scan",lambda self:snapshot())
    client=TestClient(app_module.app)
    assert client.get("/api/latest-scan").status_code==401
    headers={"X-Access-Token":"fixture-access"}
    result=client.get("/api/latest-scan",headers=headers)
    assert result.json()["source"]=="PERSISTED_UNIVERSE_SCAN"
    assert len(result.json()["snapshot"]["setups"])==2
    def failed(self): raise RuntimeError("private database URL credential")
    monkeypatch.setattr(UniverseScanStore,"latest_scan",failed)
    result=client.get("/api/latest-scan",headers=headers)
    assert result.status_code==503
    assert "credential" not in result.text and "private" not in result.text


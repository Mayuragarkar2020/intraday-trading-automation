import json

from src import run_universe_research as module
from src.run_scheduled_research import main as scheduled_main


def test_disabled_path_never_accesses_database_or_sources(monkeypatch,capsys):
    monkeypatch.delenv("UNIVERSE_SCAN_ENABLED",raising=False)
    assert module.main()==0
    assert json.loads(capsys.readouterr().out)["status"]=="UNIVERSE_SCAN_DISABLED"


def test_opt_in_dispatch_does_not_change_default_flag(monkeypatch):
    calls=[]
    monkeypatch.setenv("UNIVERSE_SCAN_ENABLED","true")
    monkeypatch.setattr(module,"main",lambda:calls.append("FULL_POOL") or 0)
    assert scheduled_main()==0 and calls==["FULL_POOL"]


def test_premarket_preserves_existing_refresh_before_warmup(monkeypatch):
    from test_universe_scanner import at
    calls=[]
    monkeypatch.setattr(module,"run_cycle",lambda *args:calls.append("PUBLISH") or {"status":"UNIVERSE_READY"})
    monkeypatch.setattr(module,"warm_universe_references",lambda *args:calls.append("WARMUP") or {"status":"SCANNED"})
    assert module.execute_cycle(at("08:45:10"),"sqlite:///unused","token")["status"]=="SCANNED"
    assert calls==["PUBLISH","WARMUP"]


def test_intraday_uses_full_pool_and_preserves_existing_recorder(monkeypatch):
    from test_universe_scanner import at
    calls=[]
    def forbidden(*args): raise AssertionError("No intraday universe rebuild")
    monkeypatch.setattr(module,"run_cycle",forbidden)
    monkeypatch.setattr(module,"run_universe_scan",lambda *args:calls.append("SCAN_POOL") or {"status":"SCANNED"})
    monkeypatch.setattr(module,"capture_once",lambda *args:calls.append("CAPTURE") or {"status":"CAPTURED","report":{"status":"FRESH_OBSERVATION"}})
    result=module.execute_cycle(at(),"sqlite:///unused","token",capture_enabled=True)
    assert calls==["SCAN_POOL","CAPTURE"]
    assert result["forward_capture"]=="FRESH_OBSERVATION"


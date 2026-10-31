import copy
import csv
import io
import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.research_csv import export_research_csv

ROOT=Path(__file__).resolve().parents[1]

def payload():
    report=json.loads((ROOT/"research/2026-10-30/universe.json").read_text(encoding="utf-8"))
    return {"snapshot":report,"source":"DATED_NSE_RESEARCH_SNAPSHOT","target_matches_today":False}

def test_csv_contains_only_research_pool_and_explicit_dates():
    rows=list(csv.DictReader(io.StringIO(export_research_csv(payload()))))
    assert len(rows)==103
    assert not {"WELCORP","ESDS","LALITHAA","LIQUIDBEES","TECHM","SHRIRAMFIN"} & {r["symbol"] for r in rows}
    assert all(r["target_date"]=="2026-11-02" and r["asof_date"]=="2026-10-30" for r in rows)
    assert all(r["execution_enabled"]=="False" for r in rows)
    assert all(r["target_matches_today"]=="False" for r in rows)

def test_csv_neutralizes_spreadsheet_formula_text():
    value=payload()
    row=next(r for r in value["snapshot"]["candidates"] if r["reference_review_status"]=="HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE")
    row["symbol"]="=UNTRUSTED"
    rows=list(csv.DictReader(io.StringIO(export_research_csv(value))))
    assert rows[0]["symbol"]=="'=UNTRUSTED"

def test_csv_endpoint_requires_token_and_disables_caching(monkeypatch):
    from src.cloud_app import app
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test-csv-token")
    monkeypatch.delenv("SCAN_DATABASE_URL",raising=False)
    client=TestClient(app)
    assert client.get("/api/universe-research.csv").status_code==401
    result=client.get("/api/universe-research.csv",headers={"X-Access-Token":"test-csv-token"})
    assert result.status_code==200
    assert result.headers["cache-control"]=="no-store"
    assert "research-universe-2026-11-02.csv" in result.headers["content-disposition"]
    assert len(list(csv.DictReader(io.StringIO(result.text))))==103

def test_cockpit_javascript_syntax():
    import re
    import shutil
    import subprocess
    import pytest
    node=shutil.which("node")
    if not node:
        pytest.skip("Node parser unavailable outside CI")
    html=(ROOT/"src/static/cockpit.html").read_text(encoding="utf-8")
    script=re.search(r"<script>([\s\S]*?)</script>",html).group(1)
    result=subprocess.run([node,"--check"],input=script,text=True,capture_output=True)
    assert result.returncode==0,result.stderr

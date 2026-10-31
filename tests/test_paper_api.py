import csv
import io
import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
import pytest
from src.paper_routes import create_paper_router
from src.paper_engine import replay
from src.paper_models import ReplayRequest
from src.paper_scenarios import example_request
from src.paper_store import PaperStore

HEAD={"X-Access-Token":"paper-test"}

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("SCAN_DATABASE_URL","sqlite:///"+str(tmp_path/"paper.db"))
    app=FastAPI()
    def auth(x_access_token: str|None=Header(default=None)):
        if x_access_token!="paper-test":raise HTTPException(401,"Denied")
    app.include_router(create_paper_router(auth))
    return TestClient(app)

def test_all_paper_endpoints_require_auth(client):
    for path in ["scenarios","runs","runs/"+"a"*64,"runs/"+"a"*64+"/trades.csv"]:
        assert client.get("/api/paper/"+path).status_code==401
    assert client.post("/api/paper/replay",json=example_request()).status_code==401
    assert client.post("/api/orders",json={}).status_code==404

def test_persisted_run_idempotence_and_restart_readback(client):
    first=client.post("/api/paper/replay",json=example_request(),headers=HEAD)
    assert first.status_code==200 and first.headers["cache-control"]=="no-store"
    assert first.json()["persisted"] and not first.json()["duplicate"]
    second=client.post("/api/paper/replay",json=example_request(),headers=HEAD).json()
    assert second["duplicate"] and second["result"]==first.json()["result"]
    store=PaperStore(os.environ["SCAN_DATABASE_URL"])
    assert len(store.recent())==1
    rid=first.json()["result"]["run_id"]
    assert store.get(rid)["input"]["source"]=="SYNTHETIC"
    assert client.get("/api/paper/runs/"+rid,headers=HEAD).json()["result"]==first.json()["result"]
    export=client.get("/api/paper/runs/"+rid+"/trades.csv",headers=HEAD)
    assert export.headers["cache-control"]=="no-store"
    assert list(csv.DictReader(io.StringIO(export.text)))[0]["symbol"]=="EXAMPLE"

def test_empty_journal_does_not_require_schema_write(client):
    assert client.get("/api/paper/runs",headers=HEAD).json()["runs"]==[]

def test_stateless_mode_is_explicit(client,monkeypatch):
    monkeypatch.delenv("SCAN_DATABASE_URL")
    result=client.post("/api/paper/replay",json=example_request(),headers=HEAD).json()
    assert not result["persisted"] and "not configured" in result["persistence_note"]

def test_database_outage_is_safe_and_does_not_disclose_connection(client,monkeypatch):
    monkeypatch.setenv("SCAN_DATABASE_URL","private-secret-not-a-db")
    response=client.post("/api/paper/replay",json=example_request(),headers=HEAD)
    assert response.status_code==503 and "private-secret" not in response.text

def test_bad_input_and_large_body_rejected(client):
    assert client.post("/api/paper/replay",content="{broken",headers=HEAD).status_code==422
    assert client.post("/api/paper/replay",content="x"*2000001,headers=HEAD).status_code==413
    assert client.get("/api/paper/runs/not-valid",headers=HEAD).status_code==404

def test_export_neutralizes_formula_like_symbols(client):
    data=example_request();data["plans"][0]["symbol"]="-EXAMPLE"
    result=client.post("/api/paper/replay",json=data,headers=HEAD).json()["result"]
    export=client.get("/api/paper/runs/"+result["run_id"]+"/trades.csv",headers=HEAD)
    assert list(csv.DictReader(io.StringIO(export.text)))[0]["symbol"]=="'-EXAMPLE"

def test_postgres_concurrent_retry_is_append_only():
    url=os.environ.get("TEST_UNIVERSE_DATABASE_URL")
    if not url:pytest.skip("PostgreSQL integration runs in CI")
    from uuid import uuid4
    data=example_request();data["label"]="Concurrency "+uuid4().hex
    request=ReplayRequest.model_validate(data);result=replay(request)
    with ThreadPoolExecutor(max_workers=4) as pool:
        inserted=list(pool.map(lambda _:PaperStore(url).save(request,result),range(4)))
    assert sum(inserted)==1
    assert PaperStore(url).get(result["run_id"])["result"]==result

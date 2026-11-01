from fastapi import FastAPI,Header,HTTPException
from fastapi.testclient import TestClient
import pytest
from src.paper_choice_routes import create_choice_router
from tests.test_paper_choice import seed
from tests.test_universe_scanner import at

HEAD={"X-Access-Token":"choice-test"}


@pytest.fixture
def client(tmp_path,monkeypatch):
    url="sqlite:///"+str(tmp_path/"api-choice.db");store,ids=seed(url)
    monkeypatch.setenv("SCAN_DATABASE_URL",url)
    def auth(x_access_token:str|None=Header(default=None)):
        if x_access_token!="choice-test":raise HTTPException(401,"Denied")
    app=FastAPI();app.include_router(create_choice_router(auth,clock=lambda:at("09:45:20")))
    return TestClient(app),ids


def test_auth_and_explicit_non_execution_mode(client):
    c,ids=client
    assert c.get("/api/paper/workspace").status_code==401
    assert c.post("/api/paper/choice",json={}).status_code==401
    result=c.get("/api/paper/workspace",headers=HEAD)
    assert result.headers["cache-control"]=="no-store"
    assert not result.json()["execution_enabled"] and len(result.json()["candidates"])==2
    command=dict(action="CHOOSE",receipt_id=ids[0],request_id="choice1",expected_choice_id=None)
    response=c.post("/api/paper/choice",json=command,headers=HEAD)
    assert response.status_code==200 and response.json()["status"]=="SELECTED_HELD"
    assert c.post("/api/paper/choice",json=command,headers=HEAD).json()["duplicate"]
    command["request_id"]="choice2"
    assert c.post("/api/paper/choice",json=command,headers=HEAD).status_code==409


@pytest.mark.parametrize("extra",[{"account_id":"reset"},{"entry":"1"},{"timestamp_verified":True}])
def test_caller_cannot_inject_account_prices_or_clearance(client,extra):
    c,ids=client
    command=dict(action="CHOOSE",receipt_id=ids[0],request_id="choice1",**extra)
    assert c.post("/api/paper/choice",json=command,headers=HEAD).status_code==422

"""CI-only browser checks using the actual replay engine, no broker/network."""
import json
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright, expect
from src.paper_models import ReplayRequest
from src.paper_engine import replay
from src.paper_scenarios import scenario_suite
from src.paper_store import PaperStore

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/"src/static/cockpit.html").read_text()
universe=json.loads((ROOT/"research/2026-10-30/universe.json").read_text())
with tempfile.TemporaryDirectory() as directory, sync_playwright() as p:
    store=PaperStore("sqlite:///"+str(Path(directory)/"paper.db"))
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":1368,"height":900})
    errors=[];calls=[]
    page.on("pageerror",lambda error:errors.append(str(error)))
    def serve(route):
        req=route.request;path=req.url.split("cockpit.test",1)[-1];calls.append(path)
        if path=="/":route.fulfill(body=html,content_type="text/html");return
        if req.headers.get("x-access-token")!="fixture-preview":route.fulfill(status=401,json={"detail":"Denied"});return
        if path=="/api/status":route.fulfill(json={"execution_enabled":False});return
        if path=="/api/universe-research":route.fulfill(json={"snapshot":universe,"source":"DATED_NSE_RESEARCH_SNAPSHOT","live":False,"execution_enabled":False,"target_matches_today":False});return
        if path=="/api/paper/scenarios":route.fulfill(json=scenario_suite());return
        if path=="/api/paper/replay":
            value=ReplayRequest.model_validate_json(req.post_data);result=replay(value);inserted=store.save(value,result)
            route.fulfill(json={"result":result,"input":value.model_dump(mode="json"),"persisted":True,"duplicate":not inserted,"persistence_note":"Saved fixture paper run"});return
        if path=="/api/paper/runs":route.fulfill(json={"runs":store.recent(),"persistent":True,"execution_enabled":False});return
        if path.startswith("/api/paper/runs/"):route.fulfill(json=store.get(path.rsplit("/",1)[-1]));return
        route.fulfill(status=503,json={"detail":"Fixture only"})
    page.route("**/*",serve);page.goto("http://cockpit.test/")
    expect(page.locator("#paperRun")).to_be_disabled()
    page.get_by_label("Access token",exact=True).fill("fixture-preview")
    page.get_by_role("button",name="Unlock workspace",exact=True).click()
    assert not any("/paper/" in c for c in calls)
    page.get_by_role("button",name="Paper lab",exact=True).click()
    page.locator("#paperSuite").click()
    expect(page.locator("#paperSuiteStatus")).to_contain_text("14 / 14")
    page.locator("#paperExample").click()
    expect(page.locator("#paperInput")).not_to_have_value("")
    page.locator("#paperRun").click()
    expect(page.locator("#paperResults")).to_be_visible()
    expect(page.locator("#paperStatus")).to_contain_text("SYNTHETIC RESULT")
    expect(page.locator("#paperTrades")).to_contain_text("EXAMPLE")
    expect(page.locator("#paperEvents")).to_contain_text("entry fill")
    with page.expect_download() as download:page.locator("#paperJson").click()
    value=json.loads(Path(download.value.path()).read_text())
    assert value["result"]["execution_enabled"] is False and value["input"]["source"]=="SYNTHETIC"
    with page.expect_download() as download:page.locator("#paperCsv").click()
    assert "EXAMPLE" in Path(download.value.path()).read_text()
    page.locator("#paperRun").click()
    expect(page.locator("#paperStatus")).to_contain_text("Existing identical run reused")
    page.locator("#paperHistory").click()
    expect(page.locator("#paperHistoryRows button")).to_have_count(1)
    page.locator("#paperHistoryRows button").click()
    expect(page.locator("#paperStatus")).to_contain_text("Opened saved paper run")
    Path("ui-review").mkdir(exist_ok=True)
    page.screenshot(path="ui-review/paper-desktop.png",full_page=True)
    page.set_viewport_size({"width":360,"height":800})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path="ui-review/paper-mobile.png",full_page=True)
    page.locator("#lockSession").click()
    expect(page.locator("#paperInput")).to_have_value("")
    expect(page.locator("#paperResults")).to_be_hidden()
    expect(page.locator("#paperEvents")).to_have_text("")
    expect(page.locator("#paperJson")).to_be_disabled()
    expect(page.locator("#paperHistoryRows")).not_to_contain_text("Synthetic EMA")
    assert not errors,errors
    browser.close()
print("Paper browser checks passed")

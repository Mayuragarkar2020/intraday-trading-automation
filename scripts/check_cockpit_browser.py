"""Browser regression checks against an isolated, dated research fixture."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "research/2026-10-30/universe.json").read_text())
html = (ROOT / "src/static/cockpit.html").read_text()
requests = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1368, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    def serve(route):
        request = route.request
        path = request.url.split("cockpit.test", 1)[-1]
        requests.append(path)
        if path == "/":
            route.fulfill(body=html, content_type="text/html")
            return
        if request.headers.get("x-access-token") != "fixture-preview":
            route.fulfill(status=401, json={"detail": "Denied"})
            return
        payload = {
            "/api/dhan-chart-reconciliation": {"status": "SAMPLE_MATCHED", "matching_convention": "OPEN", "candidates": {"OPEN": {"raw_timestamp_ist": "2026-10-30T09:15:00+05:30", "present": True, "ohlc": {"open": "1170.40", "high": "1174.60", "low": "1162.70", "close": "1164.30"}}}, "forward_paper_ready": False, "execution_enabled": False},
            "/api/status": {"mode": "PREVIEW_ONLY", "execution_enabled": False},
            "/api/universe-research": {"snapshot": report, "source": "DATED_NSE_RESEARCH_SNAPSHOT", "live": False, "execution_enabled": False, "target_matches_today": False, "availability": "Design preview · saved dated fixture"},
            "/api/latest-scan": {"snapshot": None, "status": "NO_SCANS", "live": False, "execution_enabled": False},
            "/api/demo-setups": {"setups": [{"symbol": "EXAMPLE", "status": "WAIT"}], "live": False, "execution_enabled": False},
        }
        if path == "/api/universe-research.csv":
            pool = [r["symbol"] for r in report["candidates"] if r["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"]
            route.fulfill(body="symbol\n" + "\n".join(pool), content_type="text/csv", headers={"Content-Disposition": 'attachment; filename="research.csv"'})
        elif path in payload:
            route.fulfill(json=payload[path])
        else:
            route.fulfill(status=503, json={"detail": "Fixture only"})
    page.route("**/*", serve)
    page.goto("http://cockpit.test/")
    expect(page.locator("#universeCsv")).to_be_disabled()
    expect(page.locator("#dhanReconcile")).to_be_disabled()
    page.get_by_label("Access token", exact=True).fill("fixture-preview")
    page.get_by_role("button", name="Unlock workspace", exact=True).click()
    expect(page.locator("#statPool")).to_have_text("103")
    assert "/api/demo-setups" not in requests
    assert "/api/latest-scan" not in requests
    page.locator('[data-view="universe"]').click()
    expect(page.locator("#universeRows tr")).to_have_count(12)
    expect(page.locator("#universeRows")).not_to_contain_text("LIQUIDBEES")
    page.locator("#nextPage").click()
    expect(page.locator("#universeCount")).to_contain_text("13–24 of 103")
    page.get_by_role("tab", name="On hold 2", exact=True).click()
    expect(page.locator("#universeRows tr")).to_have_count(2)
    expect(page.locator("#universeRows")).to_contain_text("TECHM")
    page.get_by_role("tab", name="Excluded 4", exact=True).click()
    expect(page.locator("#universeRows tr")).to_have_count(4)
    expect(page.locator("#universeRows")).to_contain_text("LIQUIDBEES")
    page.get_by_role("tab", name="Research pool 103", exact=True).click()
    page.locator("#universeSearch").fill("RELIANCE")
    expect(page.locator("#universeRows tr")).to_have_count(1)
    page.get_by_role("button", name="RELIANCE", exact=True).click()
    expect(page.locator("#stockDetail")).to_be_visible()
    expect(page.locator("#detailBody")).to_contain_text("INE002A01018")
    page.locator("#closeDetail").click()
    with page.expect_download() as download:
        page.locator("#universeCsv").click()
    csv_path = download.value.path()
    symbols = Path(csv_path).read_text().splitlines()[1:]
    assert len(symbols) == 103 and "LIQUIDBEES" not in symbols
    page.locator('[data-view="scanner"]').click()
    page.locator("#refresh").click()
    expect(page.locator("#refreshStatus")).to_contain_text("No stored scan")
    page.route("**/api/latest-scan",lambda route:route.fulfill(status=200,json={"status":"AVAILABLE","source":"PERSISTED_UNIVERSE_SCAN","live":False,"execution_enabled":False,"coverage":{"selected":2,"scanned":1,"complete":False},"snapshot":{"candle_close":"2026-11-02T09:45:00+05:30","setups":[{"symbol":"STOCK0","status":"ARMED","reason":"WAIT_FOR_NEXT_CANDLE_BREAKOUT","entry":"101.05","stop":"98.95"},{"symbol":"STOCK1","status":"HOLD","reason":"INVALID_OR_UNAVAILABLE_CANDLE_DATA","entry":None,"stop":None}]}}))
    page.locator("#refresh").click()
    expect(page.locator("#refreshStatus")).to_contain_text("Universe coverage: 1/2 scanned")
    expect(page.locator("#scanCoverageBadge")).to_have_text("Incomplete")
    expect(page.locator("#candidates")).to_contain_text("STOCK0")
    expect(page.locator("#candidates")).to_contain_text("Setup ready")
    expect(page.locator("#candidates")).to_contain_text("STOCK1")
    expect(page.locator("#candidates")).to_contain_text("Data held")
    page.locator('[data-view="diagnostics"]').click()
    page.locator("#dhanReconcile").click()
    expect(page.locator("#dhanReconcileResult")).to_contain_text("One candle matched exactly")
    expect(page.locator("#dhanReconcileResult")).to_contain_text("1170.40")
    expect(page.locator("#dhanReconcileResult")).to_contain_text("Forward paper trading is not ready")
    page.locator("#loadDemo").evaluate("(el) => el.closest('details').open = true")
    page.locator("#loadDemo").click()
    expect(page.locator("#demoStatus")).to_contain_text("SYNTHETIC EXAMPLE")
    expect(page.locator("#candidates")).not_to_contain_text("EXAMPLE")
    page.locator("#lockSession").click()
    expect(page.locator("#statPool")).to_have_text("—")
    expect(page.locator("#universeRows")).not_to_contain_text("RELIANCE")
    expect(page.locator("#token")).to_have_value("")
    expect(page.locator("#scanCoverageBadge")).to_have_text("Not loaded")
    expect(page.locator("#candidates")).not_to_contain_text("STOCK0")
    expect(page.locator("#dhanReconcile")).to_be_disabled()
    expect(page.locator("#dhanReconcileResult")).not_to_contain_text("1170.40")
    page.get_by_label("Access token", exact=True).fill("fixture-preview")
    page.get_by_role("button", name="Unlock workspace", exact=True).click()
    page.locator('[data-view="universe"]').click()
    expect(page.locator("#universeSearch")).to_have_value("")
    expect(page.get_by_role("tab", name="Research pool 103", exact=True)).to_have_attribute("aria-selected", "true")
    Path("ui-review").mkdir(exist_ok=True)
    page.screenshot(path="ui-review/universe-desktop.png", full_page=True)
    page.locator('[data-view="overview"]').click()
    page.screenshot(path="ui-review/overview-desktop.png", full_page=True)
    page.set_viewport_size({"width": 360, "height": 800})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path="ui-review/overview-mobile.png", full_page=True)
    page.locator('[data-view="universe"]').click()
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path="ui-review/universe-mobile.png", full_page=True)
    page.locator('[data-view="diagnostics"]').click()
    page.locator("#dhanReconcile").click()
    expect(page.locator("#dhanReconcileResult")).to_contain_text("One candle matched exactly")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path="ui-review/reconciliation-mobile.png", full_page=True)
    assert not errors, errors
    browser.close()
print("Browser regression checks passed")

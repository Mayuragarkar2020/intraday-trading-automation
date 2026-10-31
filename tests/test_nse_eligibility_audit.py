import copy
import io
import json
import pytest
from src.ingestion import DataQualityError
from src.nse_eligibility_audit import audit_eligibility, canonical_hash, fetch_sources, source_urls

def report():
    return {"mode": "LIQUIDITY_RESEARCH_ONLY", "execution_enabled": False,
            "asof_date": "2026-10-30", "target_date": "2026-11-02",
            "sources": [{"asof_date": "2026-10-01"}], "summary": {},
            "candidates": [{"symbol": "WELCORP", "isin": "INE191B01025",
                            "reference_review_status": "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"}]}

def row(symbol="OTHER", isin="INE000A01000", *, gsm=False, day="30-Oct-2026"):
    item = {"symbol": symbol, "isin": isin}
    item.update({"gsmStage": "I", "gsmTime": day} if gsm else
                {"asmSurvIndicator": "Stage I", "asmTime": day})
    return item

def evidence():
    payloads = {
        "asm": {"longterm": {"data": [row("WELCORP", "INE191B01025")]},
                "shortterm": {"data": [row()]}},
        "gsm": [row(gsm=True)], "corporate_actions": []}
    return {key: {"label": key, "url": url, "status": 200, "sha256": "0"*64,
                  "payload_sha256": canonical_hash(payloads[key]),
                  "retrieved_at": "2026-10-31T06:00:00+00:00", "payload": payloads[key]}
            for key, url in source_urls(report()).items()}

def rehash(sources):
    for value in sources.values():
        value["payload_sha256"] = canonical_hash(value["payload"])
    return sources

def test_exchange_asm_overrides_clear_broker_reference():
    original = report()
    result = audit_eligibility(original, evidence())
    assert result["candidates"][0]["reference_review_status"] == "EXCLUDED_NSE_ASM"
    assert result["summary"]["reference_research_candidate_count"] == 0
    assert result["nse_eligibility_audit"]["broker_clear_but_nse_restricted"] == ["WELCORP"]
    assert result["execution_enabled"] is False and result["tradable_count"] == 0
    assert result["restrictions_verified"] is False
    assert original["candidates"][0]["reference_review_status"].startswith("HOLD")

def test_repeated_audit_is_idempotent():
    first = audit_eligibility(report(), evidence())
    assert audit_eligibility(first, evidence()) == first

def test_absent_match_only_describes_dated_source():
    data = evidence()
    data["asm"]["payload"]["longterm"]["data"] = [row()]
    result = audit_eligibility(report(), rehash(data))
    assert result["summary"]["reference_research_candidate_count"] == 1
    assert result["candidates"][0]["nse_surveillance"]["target_effective_date_verified"] is False
    assert result["tradable_count"] == 0

def test_stale_lists_cannot_clear_absent_stock():
    data = evidence()
    data["asm"]["payload"]["longterm"]["data"] = [row(day="29-Oct-2026")]
    result = audit_eligibility(report(), rehash(data))
    assert result["candidates"][0]["reference_review_status"] == "HOLD_SURVEILLANCE_SOURCE_DATE"

def test_undated_empty_or_missing_list_fails():
    data = evidence()
    data["asm"]["payload"]["shortterm"]["data"] = []
    with pytest.raises(DataQualityError, match="empty"):
        audit_eligibility(report(), rehash(data))
    del data["asm"]["payload"]["shortterm"]
    with pytest.raises(DataQualityError, match="ASM schema"):
        audit_eligibility(report(), rehash(data))

def test_hash_tampering_rejected():
    data = evidence()
    data["gsm"]["payload"][0]["symbol"] = "ALTERED"
    with pytest.raises(DataQualityError, match="hash mismatch"):
        audit_eligibility(report(), data)

def test_future_list_rejected():
    data = evidence()
    data["gsm"]["payload"][0]["gsmTime"] = "02-Nov-2026"
    with pytest.raises(DataQualityError, match="Future"):
        audit_eligibility(report(), rehash(data))

def test_identical_restriction_duplicate_is_recorded():
    data = evidence()
    duplicate = copy.deepcopy(data["asm"]["payload"]["longterm"]["data"][0])
    duplicate["companyName"] = "Different capitalisation"
    data["asm"]["payload"]["longterm"]["data"].append(duplicate)
    result = audit_eligibility(report(), rehash(data))
    assert len(result["candidates"][0]["nse_surveillance"]["matches"]) == 1
    assert result["nse_eligibility_audit"]["identical_restriction_duplicates"]["ASM_LONGTERM"] == 1

def test_conflicting_duplicate_fails():
    data = evidence()
    duplicate = copy.deepcopy(data["asm"]["payload"]["longterm"]["data"][0])
    duplicate["asmSurvIndicator"] = "Stage II"
    data["asm"]["payload"]["longterm"]["data"].append(duplicate)
    with pytest.raises(DataQualityError, match="Conflicting"):
        audit_eligibility(report(), rehash(data))

def test_action_isin_conflict_holds_instead_of_guessing():
    data = evidence()
    data["asm"]["payload"]["longterm"]["data"] = [row()]
    data["corporate_actions"]["payload"] = [{
        "symbol": "WELCORP", "isin": "INE191B01033", "exDate": "29-Oct-2026",
        "subject": "Interim Dividend - Rs 1 Per Share"}]
    result = audit_eligibility(report(), rehash(data))
    assert result["candidates"][0]["reference_review_status"] == "HOLD_NSE_IDENTITY_CONFLICT"
    assert result["summary"]["nse_identity_conflict_count"] == 1

def test_capital_action_flagged_without_synthetic_adjustments():
    data = evidence()
    data["corporate_actions"]["payload"] = [{
        "symbol": "WELCORP", "isin": "INE191B01025", "exDate": "02-Nov-2026",
        "subject": "Bonus 1:1 and Dividend"}]
    result = audit_eligibility(report(), rehash(data))
    stock = result["candidates"][0]
    assert stock["corporate_actions"][0]["kind"] == "CAPITAL_STRUCTURE_REVIEW"
    assert stock["indicator_history_review_required"] is True
    assert stock["corporate_action_adjustments_verified"] is False

def test_action_outside_requested_window_fails():
    data = evidence()
    data["corporate_actions"]["payload"] = [{
        "symbol": "OTHER", "isin": "INE000A01000", "exDate": "03-Nov-2026",
        "subject": "Dividend"}]
    with pytest.raises(DataQualityError, match="outside"):
        audit_eligibility(report(), rehash(data))

def test_missing_source_is_not_clearance():
    data = evidence()
    del data["gsm"]
    with pytest.raises(DataQualityError, match="Missing required"):
        audit_eligibility(report(), data)

def test_source_fetch_validates_transport_and_hash():
    payloads = {item["url"]: item["payload"] for item in evidence().values()}
    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Type": "application/json"}
    def opener(request, timeout):
        assert timeout == 25 and request.full_url in payloads
        return Response(json.dumps(payloads[request.full_url]).encode())
    sources = fetch_sources(report(), opener=opener)
    assert audit_eligibility(report(), sources)["tradable_count"] == 0
    assert all(len(source["sha256"]) == 64 for source in sources.values())

def test_html_response_cannot_be_mistaken_for_empty_list():
    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Type": "text/html"}
    with pytest.raises(DataQualityError, match="JSON source"):
        fetch_sources(report(), opener=lambda *args, **kwargs: Response(b"<html>blocked</html>"))

def test_saved_live_evidence_reproduces_committed_snapshot():
    from pathlib import Path
    directory = Path(__file__).resolve().parents[1] / "research" / "2026-10-30"
    saved = json.loads((directory / "universe.json").read_text(encoding="utf-8"))
    sources = json.loads((directory / "nse-eligibility-evidence.json").read_text(encoding="utf-8"))
    assert audit_eligibility(saved, sources) == saved
    assert saved["summary"]["reference_research_candidate_count"] == 103

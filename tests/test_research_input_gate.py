import copy
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from src.research_input_gate import prepare_research_inputs

IST=ZoneInfo("Asia/Kolkata")
NOW=datetime(2026,11,2,9,45,tzinfo=IST)

@pytest.fixture
def snapshot():
    path=Path(__file__).resolve().parents[1]/"research"/"2026-10-30"/"universe.json"
    return json.loads(path.read_text(encoding="utf-8"))

def test_current_research_symbol_supplies_exact_dates(snapshot):
    result=prepare_research_inputs(snapshot,NOW,"RELIANCE","2885")
    assert result["status"]=="RESEARCH_INPUTS_READY"
    assert result["reference_dates"]==[r["asof_date"] for r in snapshot["sources"]]
    assert len(result["reference_dates"])==20
    assert result["execution_enabled"] is False
    assert result["eligibility_verified"] is False

@pytest.mark.parametrize("symbol",["WELCORP","LIQUIDBEES","TECHM","SHRIRAMFIN"])
def test_exclusions_and_identity_holds_never_feed_scanner(snapshot,symbol):
    row=next(r for r in snapshot["candidates"] if r["symbol"]==symbol)
    assert prepare_research_inputs(snapshot,NOW,symbol,row["dhan_security_id"])["status"]=="UNIVERSE_SYMBOL_HELD_OR_EXCLUDED"

def test_dated_snapshot_expires_without_auto_extension(snapshot):
    later=datetime(2026,11,3,9,45,tzinfo=IST)
    assert prepare_research_inputs(snapshot,later,"RELIANCE","2885")["status"]=="UNIVERSE_SNAPSHOT_DATE_MISMATCH"

def test_security_id_cannot_be_changed_silently(snapshot):
    assert prepare_research_inputs(snapshot,NOW,"RELIANCE","999")["status"]=="UNIVERSE_DHAN_MAPPING_MISMATCH"

def test_duplicate_candidate_is_not_selected_arbitrarily(snapshot):
    snapshot["candidates"].append(copy.deepcopy(next(r for r in snapshot["candidates"] if r["symbol"]=="RELIANCE")))
    assert prepare_research_inputs(snapshot,NOW,"RELIANCE","2885")["status"]=="UNIVERSE_SYMBOL_NOT_UNIQUE"

def test_source_hash_and_dates_required(snapshot):
    snapshot["sources"][0]["sha256"]=""
    assert prepare_research_inputs(snapshot,NOW,"RELIANCE","2885")["status"]=="UNIVERSE_REFERENCE_DATES_INVALID"

def test_unsafe_snapshot_never_approved(snapshot):
    snapshot["execution_enabled"]=True
    assert prepare_research_inputs(snapshot,NOW,"RELIANCE","2885")["status"]=="UNSAFE_UNIVERSE_SNAPSHOT"

def test_clock_must_be_timezone_aware(snapshot):
    with pytest.raises(ValueError):
        prepare_research_inputs(snapshot,NOW.replace(tzinfo=None),"RELIANCE","2885")

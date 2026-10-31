import csv
import pytest
from src.ingestion import DataQualityError
from src.universe_reference import attach_references

@pytest.fixture
def reference_files(tmp_path):
    values = [
        ("equity.csv", ["SYMBOL", " SERIES", " ISIN NUMBER"], [["ABC", "EQ", "INE000A01000"]]),
        ("bands.csv", ["Symbol", "Series", "Band"], [["ABC", "EQ", "No Band"]]),
        ("dhan.csv", ["EXCH_ID", "SEGMENT", "SERIES", "ISIN", "SECURITY_ID",
                      "ASM_GSM_FLAG", "ASM_GSM_CATEGORY", "BUY_SELL_INDICATOR"],
         [["NSE", "E", "EQ", "INE000A01000", "1", "N", "NA", "A"]])]
    paths = []
    for name, headers, rows in values:
        path = tmp_path/name
        with path.open("w", newline="") as f:
            writer = csv.writer(f); writer.writerow(headers); writer.writerows(rows)
        paths.append(path)
    return paths

def report():
    return {"candidates": [{"isin": "INE000A01000", "symbol": "ABC", "dhan_security_id": "1"}],
            "summary": {}, "execution_enabled": False, "tradable_count": 0}

def test_no_band_remains_explicit_and_does_not_grant_eligibility(reference_files):
    original = report()
    result = attach_references(original, *reference_files)
    assert result["candidates"][0]["reference_price_band"] == "No Band"
    assert result["summary"]["reference_research_candidate_count"] == 1
    assert result["candidates"][0]["reference_review_status"].startswith("HOLD")
    assert result["execution_enabled"] is False and result["tradable_count"] == 0
    assert "reference_price_band" not in original["candidates"][0]

@pytest.mark.parametrize("band", ["2", "5"])
def test_fixed_low_bands_excluded(reference_files, band):
    path = reference_files[1]
    path.write_text(path.read_text().replace("No Band", band))
    result = attach_references(report(), *reference_files)
    assert result["candidates"][0]["reference_review_status"] == "EXCLUDED_REFERENCE_LOW_BAND"
    assert result["summary"]["reference_research_candidate_count"] == 0

def test_unknown_band_holds(reference_files):
    path = reference_files[1]
    path.write_text(path.read_text().replace("No Band", "UNKNOWN"))
    assert attach_references(report(), *reference_files)["candidates"][0]["reference_review_status"] == "HOLD_PRICE_BAND_REFERENCE"

def test_symbol_isin_mismatch_holds(reference_files):
    path = reference_files[0]
    path.write_text(path.read_text().replace("ABC", "OTHER"))
    assert attach_references(report(), *reference_files)["candidates"][0]["reference_review_status"] == "HOLD_SECURITY_REFERENCE"

def test_broker_surveillance_exclusion(reference_files):
    path = reference_files[2]
    path.write_text(path.read_text().replace(",N,NA,A", ",Y,ASM,A"))
    assert attach_references(report(), *reference_files)["candidates"][0]["reference_review_status"] == "EXCLUDED_BROKER_SURVEILLANCE"

def test_duplicate_band_keys_fail(reference_files):
    path = reference_files[1]
    path.write_text(path.read_text() + "ABC,EQ,20\n")
    with pytest.raises(DataQualityError, match="Duplicate"):
        attach_references(report(), *reference_files)

def test_removed_or_unknown_surveillance_flag_holds(reference_files):
    path = reference_files[2]
    path.write_text(path.read_text().replace(",N,NA,A", ",R,NA,A"))
    assert attach_references(report(), *reference_files)["candidates"][0]["reference_review_status"] == "HOLD_BROKER_RESTRICTIONS"

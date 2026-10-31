import csv
from datetime import date, timedelta
from decimal import Decimal
import pytest
from src.ingestion import DataQualityError
from src.universe_research import build_research, validate_dates

CFG = {"universe": {"price_min": 300, "price_max": 5000, "required_history_sessions": 20},
       "liquidity": {"avg_turnover_20d_min_cr": 100, "median_turnover_20d_min_cr": 50,
                    "last_turnover_min_cr": 75, "last_to_avg_ratio_min": 0.75,
                    "min_turnover_5d_cr": 30}}
ISIN = "INE000A01000"
OTHER = "INE000B01000"
FIELDS = ["TradDt", "SctySrs", "ISIN", "TckrSymb", "ClsPric", "TtlTradgVol", "TtlTrfVal"]

@pytest.fixture
def sources(tmp_path):
    paths = []
    # Explicit fixture dates; no claim that synthetic dates verify a calendar.
    for index in range(20):
        day = (date(2026, 9, 1) + timedelta(days=index)).isoformat()
        path = tmp_path / (day + ".csv")
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(FIELDS)
            writer.writerow([day, "EQ", ISIN, "ABC", 1000, 1000000, 1200000000])
            if index == 19:
                writer.writerow([day, "EQ", OTHER, "NEW", 1000, 1000000, 1200000000])
        paths.append((day, path))
    return paths

def test_official_csv_to_research_preserves_gates_and_source_hashes(sources):
    result = build_research(sources, "2026-09-21", CFG, {ISIN: ["123"]})
    assert result["summary"]["liquidity_candidate_count"] == 1
    assert result["summary"]["incomplete_history_count"] == 1
    candidate = result["candidates"][0]
    assert candidate["symbol"] == "ABC"
    assert candidate["dhan_security_id"] == "123"
    assert Decimal(candidate["metrics"]["avg_turnover_20d_cr"]) == 120
    assert candidate["status"].startswith("HOLD")
    assert result["tradable_count"] == 0
    assert result["execution_enabled"] is False
    assert result["calendar_completeness_verified"] is False
    assert result["restrictions_verified"] is False
    assert len(result["sources"]) == 20
    assert all(len(source["sha256"]) == 64 for source in result["sources"])
    assert len(result["incomplete_histories"][0]["missing_dates"]) == 19

@pytest.mark.parametrize("mapping,status", [
    ({}, "MISSING"), ({ISIN: ["1", "2"]}, "AMBIGUOUS"),
])
def test_mapping_never_grants_eligibility(sources, mapping, status):
    result = build_research(sources, "2026-09-21", CFG, mapping)
    assert result["candidates"][0]["mapping_status"] == status
    assert "dhan_security_id" not in result["candidates"][0]
    assert result["tradable_count"] == 0

def test_future_or_target_session_is_rejected(sources):
    with pytest.raises(DataQualityError, match="precede"):
        build_research(sources, sources[-1][0], CFG)

def test_duplicate_session_is_rejected(sources):
    with pytest.raises(DataQualityError, match="distinct"):
        build_research(sources[:-1] + [sources[-2]], "2026-09-21", CFG)

def test_missing_session_file_fails_entire_run(sources):
    sources[4][1].unlink()
    with pytest.raises(FileNotFoundError):
        build_research(sources, "2026-09-21", CFG)

def test_wrong_report_date_fails_entire_run(sources):
    sources[3][1].write_text(sources[3][1].read_text().replace(sources[3][0], "2026-09-30"))
    with pytest.raises(DataQualityError, match="Date mismatch"):
        build_research(sources, "2026-09-21", CFG)

def test_short_history_and_unsorted_calendar_rejected(sources):
    with pytest.raises(DataQualityError):
        build_research(sources[1:], "2026-09-21", CFG)
    with pytest.raises(DataQualityError):
        build_research(list(reversed(sources)), "2026-09-21", CFG)

def test_latest_session_defines_membership(sources):
    path = sources[-1][1]
    path.write_text(path.read_text().replace(
        sources[-1][0] + ",EQ," + ISIN + ",ABC,1000,1000000,1200000000\n", ""))
    result = build_research(sources, "2026-09-21", CFG)
    assert result["summary"]["latest_eq_count"] == 1
    assert result["summary"]["liquidity_candidate_count"] == 0

def test_zero_volume_excludes_otherwise_liquid_stock(sources):
    path = sources[0][1]
    path.write_text(path.read_text().replace(",1000000,", ",0,"))
    result = build_research(sources, "2026-09-21", CFG)
    assert result["summary"]["liquidity_candidate_count"] == 0
    assert result["summary"]["failed_rule_counts"]["L06_VOLUME"] == 1

def test_invalid_config_history_length_rejected(sources):
    with pytest.raises(DataQualityError, match="exactly 20"):
        validate_dates([d for d, _ in sources], "2026-09-21", 5)

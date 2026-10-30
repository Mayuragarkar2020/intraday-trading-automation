from src.source_readiness import evaluate_readiness,required_sources

def test_missing_required_file_blocks_readiness():
    def checker(url):
        return {"state":"UNAVAILABLE"} if "sec_list_" in url else {"state":"AVAILABLE"}
    result=evaluate_readiness("2026-10-30","2026-10-30",checker=checker)
    assert result["status"]=="NOT_READY"
    assert not result["may_publish_trading_universe"]

def test_all_sources_still_research_only():
    result=evaluate_readiness("2026-09-25","2026-09-25",
                              checker=lambda url:{"state":"AVAILABLE"})
    assert result["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY"
    assert result["may_publish_trading_universe"] is False
    assert len(required_sources("2026-09-25","2026-09-25"))==5

from src.source_readiness import retry_readiness

def test_retry_then_ready_remains_research_only():
    calls={"n":0}
    def checker(url):
        calls["n"]+=1
        return {"state":"UNAVAILABLE"} if calls["n"]<=5 else {"state":"AVAILABLE"}
    result=retry_readiness("2026-10-30","2026-10-30",attempts=3,delay_seconds=0,checker=checker,sleep=lambda _:None)
    assert result["attempts_used"]==2
    assert result["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY"
    assert result["may_publish_trading_universe"] is False

def test_exhausted_retries_do_not_approve():
    r=retry_readiness("2026-10-30","2026-10-30",attempts=2,delay_seconds=0,
                       checker=lambda _:{"state":"UNAVAILABLE","http_status":404},
                       sleep=lambda _:None)
    assert r["status"]=="NOT_READY"
    assert r["attempts_used"]==2
    assert r["attempt_history"][-1]["http_codes"]

from src.source_readiness import validate_payload
import io
import zipfile

def test_reject_html_disguised_as_nse_csv():
    ok, reason=validate_payload("https://example.org/content/equities/sec_list_30102026.csv",b"<html>Service unavailable</html>")
    assert not ok and reason=="SCHEMA_MISMATCH"

def test_reject_corrupted_nse_zip():
    ok, reason=validate_payload("https://example.org/content/fo/BhavCopy_NSE_FO_0_0_0_20261030_F_0000.csv.zip",b"not a valid archive")
    assert not ok and reason=="INVALID_ZIP"

def test_valid_bands_csv_header():
    ok, reason=validate_payload("https://example.org/sec_list_29102026.csv",b"Symbol,Series,Security Name,Band,Remarks\\nABC,EQ,ABC,10,-\\n".replace(b"\\\\n",b"\\n"))
    assert ok and reason=="SCHEMA_VALID"

from src.source_readiness import validate_record_dates

def test_reject_wrong_date_inside_realistic_fo_zip():
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,"w") as archive:
        archive.writestr("FO.csv","TradDt,FinInstrmTp,TckrSymb\\n2026-10-29,STF,ABC\\n".replace("\\n","\n"))
    ok,reason=validate_record_dates(
        "https://example.org/BhavCopy_NSE_FO_0_0_0_20261030_F_0000.csv.zip",
        memory.getvalue(),"2026-10-30")
    assert not ok and reason=="WRONG_RECORD_DATE"

def test_accept_correct_date_inside_fo_zip():
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,"w") as archive:
        archive.writestr("FO.csv","TradDt,FinInstrmTp,TckrSymb\\n2026-10-30,STF,ABC\\n".replace("\\n","\n"))
    ok,reason=validate_record_dates(
        "https://example.org/BhavCopy_NSE_FO_0_0_0_20261030_F_0000.csv.zip",
        memory.getvalue(),"2026-10-30")
    assert ok and reason=="DATES_MATCH"

import pytest
def test_reject_unreviewed_cross_date_surveillance():
    with pytest.raises(ValueError,match="Surveillance report date differs"):
        required_sources("2026-10-30","2026-10-29")

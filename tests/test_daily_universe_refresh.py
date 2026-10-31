import copy
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
import pytest
from src.daily_universe_refresh import build_daily_universe, reference_dates_for, download_public
from src.nse_eligibility_audit import canonical_hash, source_urls

ROOT=Path(__file__).resolve().parents[1]
REL="INE002A01018"
WEL="INE191B01025"

def calendar():
    return json.loads((ROOT/"config/research_calendar.json").read_text())

def test_exact_window_rolls_without_guessing_beyond_review_horizon():
    first=reference_dates_for("2026-11-02",calendar())
    second=reference_dates_for("2026-11-03",calendar())
    assert first[0]=="2026-10-01" and first[-1]=="2026-10-30"
    assert second==first[1:]+["2026-11-02"]
    with pytest.raises(ValueError,match="CALENDAR_REVIEW_REQUIRED"):
        reference_dates_for("2026-11-09",calendar())

def test_invalid_calendar_order_rejected():
    value=calendar()
    value["sessions"]=list(reversed(value["sessions"]))
    with pytest.raises(ValueError,match="session dates"):
        reference_dates_for("2026-11-02",value)

def csv_bytes(headers,rows):
    handle=io.StringIO(newline="")
    writer=csv.writer(handle);writer.writerow(headers);writer.writerows(rows)
    return handle.getvalue().encode()

def fixture_download(wrong_date=False):
    def download(url,path,*,maximum):
        if url.endswith(".zip"):
            # Parse the literal YYYYMMDD component, not the machine clock.
            import re
            compact=re.search(r"_(\d{8})_F_",Path(path).name).group(1)
            iso=compact[:4]+"-"+compact[4:6]+"-"+compact[6:]
            if wrong_date and iso=="2026-10-29":
                iso="2026-10-28"
            data=csv_bytes(["TradDt","SctySrs","ISIN","TckrSymb","ClsPric","TtlTradgVol","TtlTrfVal"],
                           [[iso,"EQ",REL,"RELIANCE",1000,1000000,1200000000],
                            [iso,"EQ",WEL,"WELCORP",1000,1000000,1200000000]])
            buffer=io.BytesIO()
            with zipfile.ZipFile(buffer,"w") as archive:
                archive.writestr("source.csv",data)
            data=buffer.getvalue()
        elif url.endswith("EQUITY_L.csv"):
            data=csv_bytes(["SYMBOL"," SERIES"," ISIN NUMBER"],
                           [["RELIANCE","EQ",REL],["WELCORP","EQ",WEL]])
        elif url.endswith("sec_list.csv"):
            data=csv_bytes(["Symbol","Series","Band"],[["RELIANCE","EQ","No Band"],["WELCORP","EQ","20"]])
        else:
            data=csv_bytes(["EXCH_ID","SEGMENT","SECURITY_ID","ISIN","SERIES",
                           "ASM_GSM_FLAG","ASM_GSM_CATEGORY","BUY_SELL_INDICATOR"],
                          [["NSE","E","2885",REL,"EQ","N","NA","A"],
                           ["NSE","E","11821",WEL,"EQ","N","NA","A"],
                           ["BSE","D","123","IGNORED","XX","N","NA","A"]])
        Path(path).write_bytes(data)
        return {"url":url,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
    return download

def nse_evidence(report,stale=False):
    day="29-Oct-2026" if stale else "30-Oct-2026"
    generic={"symbol":"OTHER","isin":"INE000A01000"}
    payloads={
        "asm":{"longterm":{"data":[{"symbol":"WELCORP","isin":WEL,"asmTime":day,"asmSurvIndicator":"Stage I"}]},
               "shortterm":{"data":[{**generic,"asmTime":day,"asmSurvIndicator":"Stage I"}]}},
        "gsm":[{**generic,"gsmTime":day,"gsmStage":"I"}],"corporate_actions":[]}
    return {label:{"label":label,"url":url,"status":200,"sha256":"0"*64,
                   "payload_sha256":canonical_hash(payloads[label]),
                   "retrieved_at":"2026-10-31T08:00:00+00:00","payload":payloads[label]}
            for label,url in source_urls(report).items()}

def test_end_to_end_research_build_preserves_asm_precedence_and_evidence():
    report,evidence=build_daily_universe("2026-11-02",download=fixture_download(),nse_fetch=nse_evidence)
    assert report["summary"]["liquidity_candidate_count"]==2
    assert report["summary"]["reference_research_candidate_count"]==1
    assert next(r for r in report["candidates"] if r["symbol"]=="WELCORP")["reference_review_status"]=="EXCLUDED_NSE_ASM"
    assert report["execution_enabled"] is False and report["tradable_count"]==0
    assert len(evidence["public_sources"])==23
    assert len(report["config_sha256"])==64

def test_wrong_date_archive_never_becomes_snapshot():
    with pytest.raises(ValueError,match="Date mismatch"):
        build_daily_universe("2026-11-02",download=fixture_download(wrong_date=True),nse_fetch=nse_evidence)

def test_stale_surveillance_prevents_daily_publication():
    with pytest.raises(ValueError,match="SOURCE_DATE_MISMATCH"):
        build_daily_universe("2026-11-02",download=fixture_download(),
                             nse_fetch=lambda report:nse_evidence(report,stale=True))

def test_download_failure_propagates_before_any_publication():
    def failed(*args,**kwargs):
        raise ValueError("Archive unavailable")
    with pytest.raises(ValueError,match="Archive unavailable"):
        build_daily_universe("2026-11-02",download=failed,nse_fetch=nse_evidence)

def test_streaming_download_has_size_cap_and_hash(tmp_path):
    class Response(io.BytesIO):
        status=200
    path=tmp_path/"public.csv"
    metadata=download_public("https://example.test/source",path,maximum=10,
                            opener=lambda *args,**kwargs:Response(b"123456"))
    assert metadata["sha256"]==hashlib.sha256(b"123456").hexdigest()
    with pytest.raises(ValueError,match="too large"):
        download_public("https://example.test/source",path,maximum=3,
                        opener=lambda *args,**kwargs:Response(b"123456"))

"""Bounded NSE source readiness checks: no stale fallback and no order placement."""
from __future__ import annotations
import hashlib
import csv
import io
import zipfile
import time
import urllib.error
import urllib.request
from datetime import date
from src.source_dates import report_names

ROOTS={"bhavcopy":"https://nsearchives.nseindia.com/content/cm/",
       "fo_bhavcopy":"https://nsearchives.nseindia.com/content/fo/",
       "price_band_complete":"https://nsearchives.nseindia.com/content/equities/",
       "price_band_changes":"https://nsearchives.nseindia.com/content/equities/",
       "surveillance":"https://nsearchives.nseindia.com/content/cm/"}

def required_sources(asof, surveillance_date):
    date.fromisoformat(asof)
    date.fromisoformat(surveillance_date)
    names=report_names(asof,surveillance_date)
    return {k:ROOTS[k]+v for k,v in names.items()}

def validate_payload(url, raw):
    """Reject HTML error pages, corrupt archives and incompatible CSV schemas."""
    filename=url.rsplit("/",1)[-1]
    if filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                files=[n for n in archive.namelist() if n.lower().endswith(".csv")]
                if len(files)!=1 or archive.testzip() is not None:
                    return False, "INVALID_ZIP_CONTENTS"
                with archive.open(files[0]) as stream:
                    header=stream.readline().decode("utf-8-sig").strip()
        except (zipfile.BadZipFile,UnicodeError,ValueError,RuntimeError):
            return False, "INVALID_ZIP"
    else:
        try:
            header=raw.splitlines()[0].decode("utf-8-sig")
        except (IndexError,UnicodeError):
            return False, "INVALID_CSV"
    fields=set(next(csv.reader([header])))
    if filename.startswith("BhavCopy_NSE_CM_"):
        mandatory={"TradDt","TckrSymb","SctySrs","ISIN","ClsPric","TtlTradgVol","TtlTrfVal"}
    elif filename.startswith("BhavCopy_NSE_FO_"):
        mandatory={"TradDt","FinInstrmTp","TckrSymb"}
    elif filename.startswith("sec_list_"):
        mandatory={"Symbol","Series","Band"}
    elif filename.startswith("eq_band_changes_"):
        mandatory={"Symbol","Series","From","To"}
    elif filename.startswith("REG_IND"):
        mandatory={"Symbol","Series","Status","GSM"}
    else:
        return False, "UNKNOWN_SOURCE_KIND"
    return (True,"SCHEMA_VALID") if mandatory.issubset(fields) else (False,"SCHEMA_MISMATCH")

def validate_record_dates(url, raw, expected_date):
    """Verify every dated archive record matches the requested trading session."""
    filename=url.rsplit("/",1)[-1]
    if not filename.startswith(("BhavCopy_NSE_CM_","BhavCopy_NSE_FO_")):
        return True, "FILENAME_DATE_ONLY"
    if not filename.endswith(".zip"):
        return False, "EXPECTED_ZIP"
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            csvfiles=[name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csvfiles)!=1:
                return False, "INVALID_ARCHIVE_LAYOUT"
            with archive.open(csvfiles[0]) as handle:
                reader=csv.DictReader(io.TextIOWrapper(handle,encoding="utf-8-sig"))
                if "TradDt" not in (reader.fieldnames or []):
                    return False, "MISSING_TRADING_DATE"
                count=0
                for row in reader:
                    count+=1
                    if row["TradDt"].strip()!=expected_date:
                        return False, "WRONG_RECORD_DATE"
                if not count:
                    return False, "EMPTY_ARCHIVE"
        return True, "DATES_MATCH"
    except (OSError,UnicodeError,ValueError,zipfile.BadZipFile):
        return False, "INVALID_DATED_ARCHIVE"

def check_one(url, opener=None, expected_date=None):
    opener=opener or urllib.request.urlopen
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with opener(req,timeout=35) as res:
            raw=res.read(15_000_001)
            if not raw or len(raw)>15_000_000:
                return {"state":"INVALID_SIZE"}
            valid,integrity=validate_payload(url,raw)
            if not valid:
                return {"state":"INVALID_CONTENT","reason":integrity,"size_bytes":len(raw)}
            if expected_date is not None:
                dates_valid,date_check=validate_record_dates(url,raw,expected_date)
                if not dates_valid:
                    return {"state":"INVALID_CONTENT","reason":date_check,"size_bytes":len(raw)}
            else:
                date_check="DATE_NOT_CHECKED"
            return {"state":"AVAILABLE","integrity":integrity,"date_check":date_check,"size_bytes":len(raw),
                    "sha256":hashlib.sha256(raw).hexdigest()}
    except urllib.error.HTTPError as exc:
        return {"state":"UNAVAILABLE","http_status":exc.code}
    except (OSError,TimeoutError) as exc:
        return {"state":"UNAVAILABLE","error_type":type(exc).__name__}

def evaluate_readiness(asof, surveillance_date, checker=check_one):
    checks={key:{"url":url,**(checker(url,expected_date=asof) if checker is check_one else checker(url))}
            for key,url in required_sources(asof,surveillance_date).items()}
    ready=all(item["state"]=="AVAILABLE" for item in checks.values())
    return {"asof_date":asof,"surveillance_report_date":surveillance_date,
            "status":"SOURCES_AVAILABLE_RESEARCH_ONLY" if ready else "NOT_READY",
            "may_publish_trading_universe":False,"checks":checks}

def retry_readiness(asof, surveillance_date, attempts=3, delay_seconds=10, checker=check_one, sleep=time.sleep):
    """Bounded retries for unavailable reports; no stale-source fallback.

    HTTP 404 can be delayed publication, so subsequent tries are permitted.
    The final result always includes number of attempts and a trace of states.
    """
    if not 1 <= attempts <= 5 or not 0 <= delay_seconds <= 60:
        raise ValueError("Unbounded or invalid retry policy")
    history=[]
    for attempt in range(1, attempts+1):
        report=evaluate_readiness(asof,surveillance_date,checker=checker)
        history.append({"attempt":attempt,
                        "states":{k:v["state"] for k,v in report["checks"].items()},
                        "http_codes":{k:v.get("http_status") for k,v in report["checks"].items()
                                      if "http_status" in v}})
        if report["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY":
            break
        if attempt<attempts:
            sleep(delay_seconds)
    report["attempts_used"]=len(history)
    report["attempt_history"]=history
    report["may_publish_trading_universe"]=False
    return report

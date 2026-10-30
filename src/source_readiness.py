"""Bounded NSE source readiness checks: no stale fallback and no order placement."""
from __future__ import annotations
import hashlib
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

def check_one(url, opener=None):
    opener=opener or urllib.request.urlopen
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with opener(req,timeout=35) as res:
            raw=res.read(15_000_001)
            if not raw or len(raw)>15_000_000:
                return {"state":"INVALID_SIZE"}
            return {"state":"AVAILABLE","size_bytes":len(raw),
                    "sha256":hashlib.sha256(raw).hexdigest()}
    except urllib.error.HTTPError as exc:
        return {"state":"UNAVAILABLE","http_status":exc.code}
    except (OSError,TimeoutError) as exc:
        return {"state":"UNAVAILABLE","error_type":type(exc).__name__}

def evaluate_readiness(asof, surveillance_date, checker=check_one):
    checks={key:{"url":url,**checker(url)}
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

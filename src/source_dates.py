"""NSE archive path convention with explicit report-date policy.

Surveillance REG_IND250926.csv corresponds to 2026-09-25 session;
actual publication time and applicability must be independently verified. Caller must provide
an explicit surveillance report session date until publication rules are validated.
"""
from datetime import date,datetime

def iso(value):
    return date.fromisoformat(value).isoformat()

def report_names(asof, surveillance_report_date):
    iso(asof);iso(surveillance_report_date)
    d=datetime.strptime(asof,"%Y-%m-%d").strftime("%d%m%Y")
    s=datetime.strptime(surveillance_report_date,"%Y-%m-%d").strftime("%d%m%y")
    compact=asof.replace("-","")
    return {
        "bhavcopy":f"BhavCopy_NSE_CM_0_0_0_{compact}_F_0000.csv.zip",
        "fo_bhavcopy":f"BhavCopy_NSE_FO_0_0_0_{compact}_F_0000.csv.zip",
        "price_band_complete":f"sec_list_{d}.csv",
        "price_band_changes":f"eq_band_changes_{d}.csv",
        "surveillance":f"REG_IND{s}.csv",
    }

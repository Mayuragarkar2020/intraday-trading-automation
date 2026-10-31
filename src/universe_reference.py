"""Attach current public reference evidence; never infer target-date clearance."""
import copy
import csv
import hashlib
from pathlib import Path
from src.ingestion import DataQualityError

def _rows(path, required, row_filter=None):
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = [h.strip() for h in (reader.fieldnames or [])]
        if len(headers) != len(set(headers)) or not required.issubset(headers):
            raise DataQualityError("Unrecognized reference schema")
        for row in reader:
            normalized = {key.strip(): (value or "").strip() for key, value in row.items()
                          if key is not None}
            if row_filter is None or row_filter(normalized):
                rows.append(normalized)
    if not rows:
        raise DataQualityError("Empty reference")
    return rows, {"filename": path.name, "sha256": digest.hexdigest(),
                  "effective_date_verified": False}

def _unique(rows, key):
    result = {}
    for row in rows:
        value = key(row)
        if value in result:
            raise DataQualityError("Duplicate reference key")
        result[value] = row
    return result

def attach_references(report, equity_master, price_bands, dhan_master):
    equities, equity_source = _rows(equity_master, {"SYMBOL", "SERIES", "ISIN NUMBER"})
    bands, bands_source = _rows(price_bands, {"Symbol", "Series", "Band"})
    broker, broker_source = _rows(dhan_master, {
        "EXCH_ID", "SEGMENT", "SERIES", "ISIN", "SECURITY_ID",
        "ASM_GSM_FLAG", "ASM_GSM_CATEGORY", "BUY_SELL_INDICATOR"},
        row_filter=lambda row: (row["EXCH_ID"], row["SEGMENT"], row["SERIES"]) == ("NSE", "E", "EQ"))
    eq_by_isin = _unique([r for r in equities if r["SERIES"] == "EQ"],
                         lambda r: r["ISIN NUMBER"])
    bands_by_symbol = _unique([r for r in bands if r["Series"] == "EQ"],
                             lambda r: r["Symbol"])
    broker_by_isin = {}
    for row in broker:
        if (row["EXCH_ID"], row["SEGMENT"], row["SERIES"]) == ("NSE", "E", "EQ"):
            broker_by_isin.setdefault(row["ISIN"], []).append(row)
    result = copy.deepcopy(report)
    for row in result["candidates"]:
        equity = eq_by_isin.get(row["isin"])
        band = bands_by_symbol.get(row["symbol"], {}).get("Band")
        matches = broker_by_isin.get(row["isin"], [])
        row["reference_price_band"] = band
        if band in {"2", "5"}:
            status = "EXCLUDED_REFERENCE_LOW_BAND"
        elif not equity or equity["SYMBOL"] != row["symbol"]:
            status = "HOLD_SECURITY_REFERENCE"
        elif band not in {"10", "20", "No Band"}:
            status = "HOLD_PRICE_BAND_REFERENCE"
        elif len(matches) != 1 or matches[0]["SECURITY_ID"] != row.get("dhan_security_id"):
            status = "HOLD_DHAN_MAPPING"
        elif matches[0]["ASM_GSM_FLAG"] == "Y":
            status = "EXCLUDED_BROKER_SURVEILLANCE"
        elif (matches[0]["ASM_GSM_FLAG"], matches[0]["ASM_GSM_CATEGORY"],
              matches[0]["BUY_SELL_INDICATOR"]) != ("N", "NA", "A"):
            status = "HOLD_BROKER_RESTRICTIONS"
        else:
            status = "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"
        row["reference_review_status"] = status
    result["reference_sources"] = {
        "nse_equities": equity_source, "nse_price_bands": bands_source, "dhan_master": broker_source}
    result["summary"]["reference_research_candidate_count"] = sum(
        r["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"
        for r in result["candidates"])
    result["tradable_count"] = 0
    result["execution_enabled"] = False
    return result

"""Strict NSE UDiFF CM bhavcopy ingestion from manually supplied official files.

No guessed fields, silent fallbacks, or remote scraping. Preserves source SHA-256.
"""
from __future__ import annotations
import csv
import hashlib
import io
import zipfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELDS = {
    "symbol": "TckrSymb",
    "series": "SctySrs",
    "isin": "ISIN",
    "date": "TradDt",
    "close": "ClsPric",
    "volume": "TtlTradgVol",
    "turnover": "TtlTrfVal",
}

class DataQualityError(ValueError):
    pass

def _read_csv_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = [n for n in archive.namelist() if n.lower().endswith(".csv") and not n.startswith("__MACOSX")]
            if len(names) != 1:
                raise DataQualityError(f"Expected exactly one CSV in {path.name}, found {len(names)}")
            return archive.read(names[0])
    if path.suffix.lower() != ".csv":
        raise DataQualityError("Only .csv and .zip NSE reports are supported")
    return raw

def _decimal(value: str, field: str) -> Decimal:
    try:
        x = Decimal(str(value).strip().replace(",", ""))
    except (InvalidOperation, TypeError):
        raise DataQualityError(f"Invalid numeric value for {field}: {value!r}")
    if not x.is_finite() or x < 0:
        raise DataQualityError(f"Negative/nonfinite {field}: {value!r}")
    return x

def load_bhavcopy(path: str | Path, expected_date: str) -> tuple[list[dict], dict]:
    """Return EQ rows and source manifest. Date is ISO YYYY-MM-DD."""
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    data = _read_csv_bytes(path).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(data))
    headers = set(reader.fieldnames or [])
    missing = set(FIELDS.values()) - headers
    if missing:
        raise DataQualityError(f"Missing required UDiFF columns: {sorted(missing)}")
    out = []
    seen = set()
    for row_no, row in enumerate(reader, start=2):
        if row["SctySrs"].strip().upper() != "EQ":
            continue
        try:
            actual_date = datetime.strptime(row["TradDt"].strip(), "%Y-%m-%d").date().isoformat()
        except ValueError:
            raise DataQualityError(f"Invalid date in row {row_no}")
        if actual_date != expected_date:
            raise DataQualityError(f"Date mismatch in row {row_no}: {actual_date} != {expected_date}")
        symbol = row["TckrSymb"].strip()
        isin = row["ISIN"].strip()
        if not symbol or len(isin) != 12:
            raise DataQualityError(f"Invalid symbol/ISIN at row {row_no}")
        key = (isin, actual_date)
        if key in seen:
            raise DataQualityError(f"Duplicate ISIN/session: {key}")
        seen.add(key)
        close = _decimal(row["ClsPric"], "close")
        volume = _decimal(row["TtlTradgVol"], "volume")
        turnover = _decimal(row["TtlTrfVal"], "turnover")
        if close <= 0 or volume != volume.to_integral_value():
            raise DataQualityError(f"Invalid close/quantity in row {row_no}")
        out.append({"symbol": symbol, "isin": isin, "date": actual_date,
                    "close": close, "volume": int(volume), "turnover_inr": turnover})
    if not out:
        raise DataQualityError("No valid EQ records")
    return out, {"filename": path.name, "sha256": digest,
                 "asof_date": expected_date, "eq_rows": len(out)}

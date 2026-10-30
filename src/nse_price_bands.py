"""Official NSE price-band files: verified historical schema, fail closed."""
import csv
from pathlib import Path
from decimal import Decimal, InvalidOperation

COMPLETE_COLS = {"Symbol","Series","Security Name","Band","Remarks"}
CHANGES_COLS = {"Sr. No","Symbol","Series","Security Name","From","To"}

class PriceBandError(ValueError):
    pass

def _band(value):
    val=value.strip().upper().replace("%","")
    if val in {"", "-", "NA", "N/A", "NO BAND"}:
        return None
    try:
        n=Decimal(val)
    except InvalidOperation:
        raise PriceBandError(f"Unrecognized price band: {value!r}")
    if n not in {Decimal(2),Decimal(5),Decimal(10),Decimal(20)}:
        raise PriceBandError(f"Unrecognized band category: {value!r}")
    return int(n)

def parse_complete(path):
    result={}
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        if not COMPLETE_COLS.issubset(rd.fieldnames or []):
            raise PriceBandError("Complete list schema changed")
        for r in rd:
            if r["Series"].strip()!="EQ":
                continue
            key=r["Symbol"].strip()
            if not key or key in result:
                raise PriceBandError("Missing or duplicated EQ symbol")
            result[key]=_band(r["Band"])
    if not result:
        raise PriceBandError("Complete list contains no EQ rows")
    return result

def parse_changes(path):
    result={}
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        if not CHANGES_COLS.issubset(rd.fieldnames or []):
            raise PriceBandError("Change list schema changed")
        for r in rd:
            if r["Series"].strip()!="EQ":
                continue
            key=r["Symbol"].strip()
            if not key or key in result:
                raise PriceBandError("Missing or duplicated EQ change symbol")
            result[key]=(_band(r["From"]), _band(r["To"]))
    return result

def classify(symbol, complete, changes, historical_fo_symbols=None):
    if symbol in changes:
        previous, upcoming=changes[symbol]
        if symbol in complete and complete[symbol]!=previous:
            return "HOLD_INCONSISTENT_BAND"
        band=upcoming
    elif symbol in complete:
        band=complete[symbol]
    else:
        return "HOLD_BAND_NOT_LISTED"
    if band is None:
        # NSE No Band may denote F&O underlyings subject to dynamic operating ranges.
        # A date-consistent F&O constituent source is essential before classifying.
        if historical_fo_symbols is not None and symbol in historical_fo_symbols:
            return "DYNAMIC_BAND_FO_RESEARCH_ONLY"
        return "HOLD_FO_MEMBERSHIP_UNVERIFIED"
    return "EXCLUDED_NARROW_BAND" if band in (2,5) else "BAND_SCREEN_PASSED"

"""Fail closed for independently reviewed exchange controls."""
import csv
import hashlib
from pathlib import Path

class ControlError(ValueError):
    pass

def read_control(path, target_date):
    """Input: normalized, verified isin,target_date,action,reason CSV.
    This does not parse NSE raw source reports.
    """
    path=Path(path)
    with path.open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        if not {"isin","target_date","action","reason"}.issubset(rd.fieldnames or []):
            raise ControlError("Unverified restriction schema")
        result={}
        for row in rd:
            if row["target_date"].strip()!=target_date:
                continue
            isin=row["isin"].strip().upper()
            action=row["action"].strip().upper()
            reason=row["reason"].strip()
            if len(isin)!=12 or action not in {"ALLOW","BLOCK","HOLD"} or isin in result:
                raise ControlError("Invalid/duplicate restriction row")
            if action!="ALLOW" and not reason:
                raise ControlError("Missing restriction reason")
            result[isin]={"action":action,"reason":reason}
    return result,{"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                   "target_date":target_date,"records":len(result)}

def combine_controls(isins, controls):
    output={}
    for isin in isins:
        entries=[c.get(isin) for c in controls]
        if any(e is None for e in entries):
            action="HOLD"
        elif any(e["action"]=="BLOCK" for e in entries):
            action="BLOCK"
        elif any(e["action"]=="HOLD" for e in entries):
            action="HOLD"
        else:
            action="ALLOW"
        output[isin]={"approved":action=="ALLOW","action":action}
    return output

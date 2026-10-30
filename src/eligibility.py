"""Conservative instrument mapping and manually reviewed restrictions."""
import csv
from collections import defaultdict

def dhan_mapping(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        required={"EXCH_ID","SEGMENT","ISIN","SERIES","SECURITY_ID"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Unverified Dhan detailed-master schema")
        by_isin=defaultdict(list)
        for r in reader:
            if (r["EXCH_ID"].strip(),r["SEGMENT"].strip(),r["SERIES"].strip()) != ("NSE","E","EQ"):
                continue
            isin=r["ISIN"].strip()
            sid=r["SECURITY_ID"].strip()
            if len(isin)==12 and sid.isdigit():
                by_isin[isin].append(sid)
        return dict(by_isin)

def reviewed_restrictions(path, target_date):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not {"isin","target_date","eligible","reason"}.issubset(reader.fieldnames or []):
            raise ValueError("Unverified restrictions schema")
        out={}
        for row in reader:
            if row["target_date"] != target_date:
                continue
            isin=row["isin"].strip()
            flag=row["eligible"].strip().upper()
            if isin in out or len(isin)!=12 or flag not in {"YES","NO"}:
                raise ValueError("Invalid or duplicate restriction decision")
            if flag=="NO" and not row["reason"].strip():
                raise ValueError("Missing rejection reason")
            out[isin]={"approved": flag=="YES","reason":row["reason"].strip()}
        return out

def reconcile(decisions, mapping, restrictions):
    out=[]
    for source in decisions:
        row=dict(source)
        if not row.get("liquidity_pass"):
            row["status"]="EXCLUDED_LIQUIDITY"
        elif len(mapping.get(row["isin"],[]))!=1:
            row["status"]="HOLD_DHAN_MAPPING"
        elif row["isin"] not in restrictions:
            row["status"]="HOLD_RESTRICTIONS"
        elif not restrictions[row["isin"]]["approved"]:
            row["status"]="EXCLUDED_RESTRICTION"
            row["restriction_reason"]=restrictions[row["isin"]]["reason"]
        else:
            row["status"]="ELIGIBLE_MANUALLY_REVIEWED"
            row["dhan_security_id"]=mapping[row["isin"]][0]
        out.append(row)
    return out

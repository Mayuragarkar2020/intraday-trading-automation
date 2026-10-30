"""Conservative parsing of actual NSE REG_IND surveillance rows.

Code 100 is interpreted as no named surveillance indicator only for fields
whose meanings have been validated; all other values HOLD pending interpretation.
"""
import csv
from pathlib import Path

COLS={"Symbol","Series","Status","GSM","Long_Term_Additional_Surveillance_Measure (Long Term ASM)","Short_Term_Additional_Surveillance_Measure (Short Term ASM)"}
FLAGS=("GSM","Long_Term_Additional_Surveillance_Measure (Long Term ASM)","Short_Term_Additional_Surveillance_Measure (Short Term ASM)")

def load_surveillance(path):
    result={}
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        if not COLS.issubset(reader.fieldnames or []):
            raise ValueError("Unknown surveillance schema")
        for row in reader:
            if row["Series"].strip().upper()!="EQ":continue
            symbol=row["Symbol"].strip()
            if not symbol or symbol in result:raise ValueError("Invalid/duplicate symbol")
            result[symbol]={key:row[key].strip() for key in COLS}
    if not result:raise ValueError("Empty surveillance report")
    return result

def classify(symbol, report):
    if symbol not in report:return "HOLD_SURVEILLANCE_NOT_FOUND"
    row=report[symbol]
    if row["Status"]!="A":return "HOLD_SECURITY_STATUS"
    # Do not infer the significance of numeric codes other than 100.
    if any(row[flag]!="100" for flag in FLAGS):
        return "HOLD_SURVEILLANCE_FLAG_REVIEW"
    return "SURVEILLANCE_BASIC_CLEAR"

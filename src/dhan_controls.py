"""Dhan detailed-master advisory controls. Source: official DhanHQ instrument list docs.

These are broker flags, NOT a replacement for effective-dated NSE controls.
"""
import csv

REQUIRED={"EXCH_ID","SEGMENT","ISIN","SERIES","SECURITY_ID",
          "ASM_GSM_FLAG","BUY_SELL_INDICATOR"}

def load_broker_controls(path):
    out={}
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError("Missing Dhan broker-control columns")
        for r in reader:
            if (r["EXCH_ID"].strip().upper(),
                r["SEGMENT"].strip().upper(),
                r["SERIES"].strip().upper())!=("NSE","E","EQ"):
                continue
            isin=r["ISIN"].strip().upper()
            if len(isin)!=12:
                continue
            if isin in out:
                raise ValueError("Duplicate NSE EQ ISIN in detailed master")
            flag=r["ASM_GSM_FLAG"].strip().upper()
            buysell=r["BUY_SELL_INDICATOR"].strip().upper()
            # Documentation defines Y=ASM/GSM, N=not ASM/GSM, A=buy and sell permitted.
            if flag=="Y":
                status="BLOCK_BROKER_SURVEILLANCE"
            elif flag!="N" or buysell!="A":
                status="HOLD_BROKER_FLAGS"
            else:
                status="BROKER_FLAGS_CLEAR"
            out[isin]={"status":status,"security_id":r["SECURITY_ID"].strip()}
    return out

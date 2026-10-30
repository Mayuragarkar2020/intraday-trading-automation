import csv
from src.dhan_controls import load_broker_controls

def test_broker_flags_fail_closed(tmp_path):
    p=tmp_path/"dhan.csv"
    with p.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["EXCH_ID","SEGMENT","ISIN","SERIES","SECURITY_ID","ASM_GSM_FLAG","BUY_SELL_INDICATOR"])
        w.writerow(["NSE","E","INE000A01000","EQ","101","Y","A"])
        w.writerow(["NSE","E","INE000B01000","EQ","102","N","A"])
        w.writerow(["NSE","E","INE000C01000","EQ","103","R","A"])
    flags=load_broker_controls(p)
    assert flags["INE000A01000"]["status"]=="BLOCK_BROKER_SURVEILLANCE"
    assert flags["INE000B01000"]["status"]=="BROKER_FLAGS_CLEAR"
    assert flags["INE000C01000"]["status"]=="HOLD_BROKER_FLAGS"

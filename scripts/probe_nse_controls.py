"""Research-only NSE restriction-source schema probe; no trading approval."""
import csv
import io
import json
import urllib.request
from datetime import datetime

FILES = {
    "price_bands": "sec_list_25092026.csv",
    "surveillance": "REG_IND250926.csv",
    "surveillance_new": "REG1_IND250926.csv",
    "next_day_changes": "eq_band_changes_25092026.csv",
}
BASE = "https://nsearchives.nseindia.com/content/cm/"

def inspect(name, filename):
    req = urllib.request.Request(BASE + filename, headers={"User-Agent":"Mozilla/5.0", "Accept":"*/*"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read(5_000_001)
    if len(data)>5_000_000 or len(data)<10:
        raise ValueError("Unexpected file size")
    sample=data[:10000].decode("utf-8-sig", errors="replace").splitlines()
    return {"file":filename,"bytes":len(data),"first_lines":sample[:3]}

def main():
    failed=0
    for name, filename in FILES.items():
        try:
            print(json.dumps({"source":name, "status":"READABLE", **inspect(name, filename)}), flush=True)
        except Exception as exc:
            failed+=1
            print(json.dumps({"source":name,"status":"NOT_VERIFIED","error":str(exc)[:200]}),flush=True)
    return int(failed>0)

if __name__=="__main__":
    raise SystemExit(main())

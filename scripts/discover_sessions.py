"""Research utility: discover prior sessions using validated NSE archive availability."""
import argparse
import json
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from src.ingestion import load_bhavcopy, DataQualityError

def discover(asof, out_dir, count=20, max_calendar_days=50):
    if count != 20:
        raise ValueError("Phase 1 requires 20 completed sessions")
    end=date.fromisoformat(asof)
    directory=Path(out_dir);directory.mkdir(parents=True,exist_ok=True)
    found=[]
    for lag in range(max_calendar_days):
        day=end-timedelta(days=lag)
        if day.weekday()>=5:
            continue
        iso=day.isoformat()
        compact=iso.replace("-","")
        name=f"BhavCopy_NSE_CM_0_0_0_{compact}_F_0000.csv.zip"
        path=directory/name
        if not path.exists():
            url=f"https://nsearchives.nseindia.com/content/cm/{name}"
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
            try:
                with urllib.request.urlopen(req,timeout=30) as res:
                    data=res.read(12_000_001)
            except urllib.error.HTTPError as exc:
                if exc.code in (404,403):
                    # 403 is NOT proof of holiday: never silently skip access denial
                    if exc.code==403:
                        raise DataQualityError(f"Forbidden archive access: {iso}") from exc
                    continue
                raise
            if len(data)>12_000_000:
                raise DataQualityError("Archive too large")
            path.write_bytes(data)
        load_bhavcopy(path,iso)
        found.append(iso)
        if len(found)==count:
            break
    if len(found)!=count or found[0]!=asof:
        raise DataQualityError(f"Could not establish {count} validated archive sessions ending {asof}")
    return sorted(found)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asof",required=True)
    p.add_argument("--directory",default="data/raw/nse")
    p.add_argument("--dates-file",default="data/sessions.txt")
    a=p.parse_args()
    days=discover(a.asof,a.directory)
    path=Path(a.dates_file);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(days)+"\n")
    print(json.dumps({"sessions":days,"source":"validated NSE archive availability","status":"RESEARCH_ONLY"}))

if __name__=="__main__":
    main()

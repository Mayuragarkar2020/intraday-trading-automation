"""Research-only NSE 20-session downloader. Explicit date list avoids guessing holidays.

Provide exactly 20 ISO exchange-session dates via a text file (oldest to newest).
Successful downloads are validated by the strict existing UDiFF parser.
"""
import argparse
import hashlib
import json
import time
import os
import tempfile
import urllib.request
from datetime import date
from pathlib import Path
from src.ingestion import load_bhavcopy, DataQualityError

BASE = "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date}_F_0000.csv.zip"

def download(dates_file, output_dir):
    days=[x.strip() for x in Path(dates_file).read_text().splitlines() if x.strip() and not x.startswith("#")]
    if len(days)!=20 or len(set(days))!=20 or days!=sorted(days):
        raise ValueError("Exactly 20 distinct ascending NSE trading session dates required")
    for day in days:
        date.fromisoformat(day)
    directory=Path(output_dir)
    directory.mkdir(parents=True,exist_ok=True)
    manifests=[]
    for day in days:
        name="BhavCopy_NSE_CM_0_0_0_"+day.replace("-","")+"_F_0000.csv.zip"
        path=directory/name
        if not path.exists():
            url=BASE.format(date=day.replace("-",""))
            request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
            with urllib.request.urlopen(request,timeout=40) as response:
                data=response.read(12_000_001)
            if len(data)>12_000_000 or len(data)<1000:
                raise DataQualityError(f"Unexpected source size for {day}")
            # Validate a private temporary archive before publishing it to the cache.
            # This prevents interrupted or malformed downloads from becoming cache hits.
            fd, temporary = tempfile.mkstemp(prefix=".nse-", suffix=".zip", dir=directory)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                _, manifest = load_bhavcopy(temporary, day)
                os.replace(temporary, path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
            time.sleep(0.4)
        else:
            # Cached files must pass the same validation as new downloads.
            _, manifest = load_bhavcopy(path, day)
        manifests.append({**manifest, "filename": path.name})
    return manifests

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--dates-file",required=True)
    p.add_argument("--output-dir",default="data/raw/nse")
    p.add_argument("--manifest",default="output/nse_source_manifest.json")
    args=p.parse_args()
    try:
        manifest=download(args.dates_file,args.output_dir)
        target=Path(args.manifest);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(manifest,indent=2))
        print(f"VALIDATED_SOURCES: {len(manifest)} sessions. NOT a tradable universe.")
    except Exception as ex:
        p.exit(2,f"NOT_READY: {type(ex).__name__}: {ex}\n")

if __name__=="__main__":
    main()

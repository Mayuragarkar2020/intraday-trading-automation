"""Non-production source probe. Reports file headers and SHA256; never trades."""
import csv
import hashlib
import io
import json
import urllib.error
import urllib.request

URLS = {
    "nse_bhavcopy": "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20260925_F_0000.csv.zip",
    "dhan_detailed": "https://images.dhan.co/api-data/api-scrip-master-detailed.csv",
}

def probe(name, url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; IntradayDataValidation/1.0)",
        "Accept": "*/*"
    })
    with urllib.request.urlopen(request, timeout=30) as res:
        data = res.read(100_000_001)
        if len(data) > 100_000_000:
            raise ValueError("Source exceeded 100MB safety cap")
    if name == "nse_bhavcopy":
        import zipfile
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if len(names) != 1:
                raise ValueError("Unexpected NSE archive layout")
            first = z.open(names[0]).readline().decode("utf-8-sig").strip()
    else:
        first = data.splitlines()[0].decode("utf-8-sig").strip()
    header = next(csv.reader([first]))
    return {"name": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "column_count": len(header), "columns": header}

def main():
    failures = 0
    for name, url in URLS.items():
        try:
            result = probe(name, url)
            print(json.dumps({"result":"ACCESSIBLE",**result}), flush=True)
        except Exception as exc:
            failures += 1
            print(json.dumps({"result":"SOURCE_UNAVAILABLE","name":name,
                              "error":f"{type(exc).__name__}: {str(exc)[:250]}"}),flush=True)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())

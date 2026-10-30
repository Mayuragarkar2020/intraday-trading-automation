"""Research-only historical F&O underlying membership from NSE UDiFF F&O bhavcopy."""
import csv,io,zipfile,urllib.request,json,hashlib
from pathlib import Path
from collections import Counter
URL="https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_20260925_F_0000.csv.zip"

def main():
    request=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(request,timeout=45) as response:
        raw=response.read(10_000_001)
    if len(raw)>10_000_000 or len(raw)<500:
        raise ValueError("Unexpected FO archive size")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1:raise ValueError("Unexpected archive layout")
        with z.open(names[0]) as f:
            reader=csv.DictReader(io.TextIOWrapper(f,encoding="utf-8-sig"))
            required={"TradDt","FinInstrmTp","TckrSymb"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("Unverified FO schema")
            counts=Counter()
            for row in reader:
                if row["TradDt"].strip()!="2026-09-25":raise ValueError("FO wrong date")
                counts[row["FinInstrmTp"].strip()]+=1
    result={"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "source_sha256":hashlib.sha256(raw).hexdigest(),
            "instrument_types":dict(counts),"source_url":URL}
    Path("output").mkdir(exist_ok=True)
    Path("output/fo_schema_probe.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
if __name__=="__main__":main()

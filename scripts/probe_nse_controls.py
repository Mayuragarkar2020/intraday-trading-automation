"""Research-only discovery of official report paths; never approves a stock."""
import json
import urllib.error
import urllib.request

FILES = {
 "price_bands":"sec_list_25092026.csv",
 "next_day_changes":"eq_band_changes_25092026.csv",
}
ROOTS = [
 "https://nsearchives.nseindia.com/content/cm/",
 "https://nsearchives.nseindia.com/content/equities/",
 "https://nsearchives.nseindia.com/content/eq_band_changes/",
 "https://nsearchives.nseindia.com/content/",
 "https://archives.nseindia.com/content/cm/",
 "https://archives.nseindia.com/content/equities/",
]
def main():
    found=0
    for name,filename in FILES.items():
        for root in ROOTS:
            url=root+filename
            try:
                request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
                with urllib.request.urlopen(request,timeout=12) as response:
                    data=response.read(1_000_001)
                if not data or len(data)>1_000_000:
                    raise ValueError("Empty or excessive file")
                lines=data.decode("utf-8-sig").splitlines()[:3]
                print(json.dumps({"source":name,"status":"READABLE","url":url,"lines":lines}),flush=True)
                found+=1
                break
            except Exception as exc:
                print(json.dumps({"source":name,"status":"NOT_FOUND_AT_CANDIDATE",
                                  "url":url,"error":str(exc)[:80]}),flush=True)
    return 0 if found==len(FILES) else 1
if __name__=="__main__":
    raise SystemExit(main())

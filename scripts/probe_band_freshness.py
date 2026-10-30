"""Probe official NSE report availability without stale fallback or approval."""
import json, urllib.request, urllib.error
from datetime import date,timedelta

ROOT="https://nsearchives.nseindia.com/content/equities/"
def probe(session):
    ds=session.strftime("%d%m%Y")
    output={}
    for category,filename in (("complete",f"sec_list_{ds}.csv"),("changes",f"eq_band_changes_{ds}.csv")):
        try:
            req=urllib.request.Request(ROOT+filename,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=20) as res:
                header=res.readline().decode("utf-8-sig").strip()
                status=res.status
            output[category]={"status":"AVAILABLE","http":status,"filename":filename,"header":header}
        except urllib.error.HTTPError as exc:
            output[category]={"status":"UNAVAILABLE","http":exc.code,"filename":filename}
        except Exception as exc:
            output[category]={"status":"UNAVAILABLE","reason":type(exc).__name__,"filename":filename}
    return output

def main():
    for s in (date(2026,10,29),date(2026,10,30)):
        print(json.dumps({"session":s.isoformat(),"sources":probe(s)}),flush=True)
if __name__=="__main__":main()

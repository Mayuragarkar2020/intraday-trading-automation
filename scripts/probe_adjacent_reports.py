"""Diagnostic only: compare adjacent dates and archive paths; never substitute."""
import json,urllib.request,urllib.error
from datetime import date,timedelta
BASES={"fo":"https://nsearchives.nseindia.com/content/fo/",
       "cm":"https://nsearchives.nseindia.com/content/cm/",
       "equities":"https://nsearchives.nseindia.com/content/equities/"}
def probe(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"*/*"})
    try:
        with urllib.request.urlopen(req,timeout=15) as res:
            return {"http":res.status,"content_type":res.headers.get("Content-Type"),"size_hint":res.headers.get("Content-Length")}
    except urllib.error.HTTPError as e:return {"http":e.code}
    except Exception as e:return {"error":type(e).__name__}
def main():
    for d in (date(2026,10,29),date(2026,10,30),date(2026,10,31),date(2026,11,2)):
        dd=d.strftime("%d%m%Y"); short=d.strftime("%d%m%y");compact=d.strftime("%Y%m%d")
        names={"fo":f"BhavCopy_NSE_FO_0_0_0_{compact}_F_0000.csv.zip",
               "band":f"sec_list_{dd}.csv",
               "surveillance":f"REG_IND{short}.csv",
               "surveillance_new":f"REG1_IND{short}.csv"}
        for key,file in names.items():
            group="fo" if key=="fo" else "equities" if key=="band" else "cm"
            print(json.dumps({"date":d.isoformat(),"type":key,"filename":file,"check":probe(BASES[group]+file)}),flush=True)
if __name__=="__main__":main()

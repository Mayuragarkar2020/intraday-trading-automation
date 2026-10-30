"""Read-only DhanHQ historical candle fetcher.

No order endpoints. Inject httpx transport to test without credentials.
The caller supplies Dhan's numeric securityId from the instrument master.
"""
from datetime import datetime, timedelta
import httpx

URL="https://api.dhan.co/v2/charts/intraday"

def fetch_intraday(access_token,security_id,interval,from_date,to_date,*,transport=None):
    if not access_token or not isinstance(access_token,str):
        raise ValueError("Missing access token")
    if not str(security_id).isdigit():
        raise ValueError("Require verified numeric security ID")
    if interval not in (1,5,15,25,60):
        raise ValueError("Unsupported interval")
    start=datetime.strptime(from_date,"%Y-%m-%d %H:%M:%S")
    end=datetime.strptime(to_date,"%Y-%m-%d %H:%M:%S")
    if end<=start or end-start>timedelta(days=90):
        raise ValueError("Invalid range (maximum 90 days)")
    payload={"securityId":str(security_id),"exchangeSegment":"NSE_EQ",
             "instrument":"EQUITY","interval":str(interval),"oi":False,
             "fromDate":from_date,"toDate":to_date}
    with httpx.Client(timeout=15,transport=transport,follow_redirects=False) as client:
        response=client.post(URL,headers={"access-token":access_token,
          "Accept":"application/json","Content-Type":"application/json"},json=payload)
        response.raise_for_status()
        data=response.json()
    if not isinstance(data,dict) or not all(isinstance(data.get(k),list)
         for k in ("timestamp","open","high","low","close","volume")):
        raise ValueError("Unexpected Dhan API response format")
    return data

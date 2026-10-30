import httpx
import pytest
from src.dhan_history_client import fetch_intraday,URL

def test_fetch_exact_read_only_endpoint_with_mock():
    seen=[]
    def handler(request):
        seen.append(request)
        assert str(request.url)==URL
        assert request.method=="POST"
        assert request.headers["access-token"]=="placeholder-test-token"
        body=__import__("json").loads(request.content)
        assert body["securityId"]=="1333"
        assert body["interval"]=="5"
        assert body["exchangeSegment"]=="NSE_EQ"
        return httpx.Response(200,json={"timestamp":[1],"open":[100],
            "high":[101],"low":[99],"close":[100],"volume":[1000]})
    data=fetch_intraday("placeholder-test-token","1333",5,
       "2026-10-20 09:15:00","2026-10-21 15:30:00",
       transport=httpx.MockTransport(handler))
    assert len(seen)==1
    assert data["close"]==[100]

def test_fail_closed_bad_security_id_and_range():
    with pytest.raises(ValueError):
        fetch_intraday("test","RELIANCE",5,"2026-10-20 09:15:00","2026-10-21 15:30:00")
    with pytest.raises(ValueError):
        fetch_intraday("test","1333",5,"2026-01-01 00:00:00","2026-10-30 00:00:00")

def test_broker_error_and_malformed_response():
    with pytest.raises(httpx.HTTPStatusError):
        fetch_intraday("test","1333",5,"2026-10-20 09:15:00","2026-10-21 15:30:00",
          transport=httpx.MockTransport(lambda r:httpx.Response(403,json={"message":"denied"})))
    with pytest.raises(ValueError):
        fetch_intraday("test","1333",5,"2026-10-20 09:15:00","2026-10-21 15:30:00",
          transport=httpx.MockTransport(lambda r:httpx.Response(200,json={"message":"bad"})))

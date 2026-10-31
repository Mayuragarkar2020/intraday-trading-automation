from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
import httpx

from src.dhan_chart_reconciliation import CLOSING_CHART_SAMPLES, reconcile_reliance_closing_chart
import src.cloud_app as module


def payload(offset=0):
    return {"timestamp":[int((t+timedelta(minutes=offset)).timestamp()) for t,_ in CLOSING_CHART_SAMPLES],
            **{k:[str(prices[k]) for _,prices in CLOSING_CHART_SAMPLES]
               for k in ("open","high","low","close")}, "volume":[100,200]}


@pytest.mark.parametrize("offset,convention",[(0,"OPEN"),(5,"CLOSE")])
def test_two_exact_matches_remain_scoped(offset,convention):
    result = reconcile_reliance_closing_chart(payload(offset))
    assert result["status"] == "ALL_SAMPLES_MATCHED"
    assert result["matching_convention"] == convention
    assert result["scope"] == "TWO_HISTORICAL_CLOSING_CANDLES_ONLY"
    assert result["raw_target_session_count"] == 2
    assert result["samples"][1]["chart_ohlc"]["close"] == "1159.00"
    assert not result["timestamp_convention_verified"]
    assert not result["cas_eligibility_verified"]
    assert not result["forward_paper_ready"] and not result["execution_enabled"]
    assert len(result["decoded_payload_sha256"]) == 64


def test_missing_one_sample_is_partial_not_full_verification():
    p = {k:v[:1] for k,v in payload().items()}
    result = reconcile_reliance_closing_chart(p)
    assert result["status"] == "PARTIAL_MATCH"
    assert result["matching_convention"] is None


def test_conflicting_timestamp_conventions_are_not_combined():
    p = payload()
    p["timestamp"][1] += 300
    result = reconcile_reliance_closing_chart(p)
    assert result["status"] == "INCONSISTENT_CONVENTIONS"
    assert result["matching_convention"] is None


def test_ambiguous_sample_does_not_confirm_convention():
    p = payload()
    for k in p:
        p[k].append(p[k][-1]+300 if k=="timestamp" else p[k][-1])
    result = reconcile_reliance_closing_chart(p)
    assert result["status"] == "AMBIGUOUS"
    assert result["matching_convention"] is None


@pytest.mark.parametrize("change",["price","other_day","missing_boundary"])
def test_mismatched_prices_or_dates_never_imply_full_match(change):
    p = payload()
    if change == "price": p["close"][1] = "1159.05"
    elif change == "other_day": p["timestamp"] = [t-86400 for t in p["timestamp"]]
    else: p["timestamp"] = [t-3600 for t in p["timestamp"]]
    result = reconcile_reliance_closing_chart(p)
    assert result["status"] != "ALL_SAMPLES_MATCHED"
    assert result["matching_convention"] is None


def test_later_raw_timestamp_is_reported_without_auction_fill_inference():
    p = payload()
    for k in p:
        p[k].append(p[k][-1]+300 if k=="timestamp" else p[k][-1])
    # Avoid matching either screenshot with the new row.
    p["close"][-1] = "1160.00"
    result = reconcile_reliance_closing_chart(p)
    assert result["status"] == "ALL_SAMPLES_MATCHED"
    assert result["raw_timestamps_at_or_after_15_15"] == ["2026-10-30T15:15:00+05:30"]
    assert result["boundary_interpretation"] == "UNVERIFIED_NO_AUCTION_FILL_INFERENCE"


@pytest.mark.parametrize("field,value",[("close","NaN"),("high","Infinity"),
    ("low",True),("volume",-1),("volume",1.2),("timestamp",None),
    ("timestamp",1.5),("open",99999)])
def test_invalid_candles_fail_closed(field,value):
    p = payload(); p[field][0] = value
    with pytest.raises(ValueError):
        reconcile_reliance_closing_chart(p)


def test_duplicate_timestamps_fail_closed():
    p = payload(); p["timestamp"][1] = p["timestamp"][0]
    with pytest.raises(ValueError): reconcile_reliance_closing_chart(p)


def test_api_auth_fixed_fetch_and_safe_failure(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","access")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","private-broker-token")
    client = TestClient(module.app)
    url = "/api/dhan-closing-chart-reconciliation"
    assert client.post(url).status_code == 401
    headers = {"X-Access-Token":"access"}
    calls = []
    def fetch(*args):
        calls.append(args); return payload()
    monkeypatch.setattr(module,"fetch_intraday",fetch)
    result = client.post(url,headers=headers)
    assert result.json()["status"] == "ALL_SAMPLES_MATCHED"
    assert calls == [("private-broker-token","2885",5,
                      "2026-10-29 09:15:00","2026-10-31 09:15:00")]
    assert "private-broker-token" not in result.text
    def broken(*args): raise httpx.ReadTimeout("private-broker-token broker message")
    monkeypatch.setattr(module,"fetch_intraday",broken)
    result = client.post(url,headers=headers)
    assert result.json()["status"] == "RECONCILIATION_FAILED"
    assert "private-broker-token" not in result.text and "broker message" not in result.text
    monkeypatch.delenv("DHAN_ACCESS_TOKEN")
    assert client.post(url,headers=headers).json()["status"] == "DHAN_TOKEN_NOT_CONFIGURED"


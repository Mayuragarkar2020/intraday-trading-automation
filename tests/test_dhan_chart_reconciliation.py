from copy import deepcopy
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from src.dhan_chart_reconciliation import CHART_OPEN, CHART_OHLC, reconcile_reliance_chart
import src.cloud_app as module


def payload(offset=0):
    return {"timestamp": [int((CHART_OPEN + timedelta(minutes=offset)).timestamp())],
            **{k: [str(v)] for k, v in CHART_OHLC.items()}, "volume": [100]}


@pytest.mark.parametrize("offset,convention", [(0, "OPEN"), (5, "CLOSE")])
def test_exact_hypothesis_match_is_scoped(offset, convention):
    result = reconcile_reliance_chart(payload(offset))
    assert result["status"] == "SAMPLE_MATCHED"
    assert result["matching_convention"] == convention
    assert not result["timestamp_convention_verified"]
    assert not result["forward_paper_ready"]
    assert not result["execution_enabled"]


def test_both_matching_hypotheses_are_ambiguous():
    first, second = payload(), payload(5)
    result = reconcile_reliance_chart({k: first[k] + second[k] for k in first})
    assert result["status"] == "AMBIGUOUS"
    assert result["matching_convention"] is None


@pytest.mark.parametrize("change", ["mismatch", "different_day", "missing_candidate"])
def test_does_not_infer_a_match(change):
    data = payload()
    if change == "mismatch":
        data["close"] = ["1164.35"]
    else:
        data["timestamp"][0] += 86400 if change == "different_day" else 600
    assert reconcile_reliance_chart(data)["status"] == "NO_MATCH"


@pytest.mark.parametrize("field,value", [("open", True), ("low", "NaN"),
    ("high", "Infinity"), ("close", 2000), ("volume", -1), ("volume", 1.5),
    ("timestamp", 1793331900000), ("timestamp", 1.5), ("timestamp", None)])
def test_invalid_inputs_fail_closed(field, value):
    data = payload()
    data[field] = [value]
    with pytest.raises(ValueError):
        reconcile_reliance_chart(data)


@pytest.mark.parametrize("kind", ["empty", "missing", "length", "duplicate", "unordered", "unaligned"])
def test_invalid_structure_and_timestamps(kind):
    data = payload()
    if kind == "empty":
        data = {k: [] for k in data}
    elif kind == "missing":
        del data["volume"]
    elif kind == "length":
        data["open"] = []
    elif kind == "unaligned":
        data["timestamp"][0] += 1
    else:
        second = deepcopy(data) if kind == "duplicate" else payload(-5)
        data = {k: data[k] + second[k] for k in data}
    with pytest.raises(ValueError):
        reconcile_reliance_chart(data)


def test_authenticated_fixed_fetch_and_safe_errors(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN", "test-access")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "test-broker-secret")
    client = TestClient(module.app)
    url = "/api/dhan-chart-reconciliation"
    assert client.post(url).status_code == 401
    headers = {"X-Access-Token": "test-access"}
    calls = []
    def fetch(*args):
        calls.append(args)
        return payload()
    monkeypatch.setattr(module, "fetch_intraday", fetch)
    response = client.post(url, headers=headers)
    assert response.json()["status"] == "SAMPLE_MATCHED"
    assert calls == [("test-broker-secret", "2885", 5,
                      "2026-10-29 09:15:00", "2026-10-31 09:15:00")]
    assert "test-broker-secret" not in response.text
    def broken(*args):
        raise ValueError("private broker response test-broker-secret")
    monkeypatch.setattr(module, "fetch_intraday", broken)
    response = client.post(url, headers=headers)
    assert response.json()["status"] == "RECONCILIATION_FAILED"
    assert "private" not in response.text and "test-broker-secret" not in response.text
    monkeypatch.delenv("DHAN_ACCESS_TOKEN")
    assert client.post(url, headers=headers).json()["status"] == "DHAN_TOKEN_NOT_CONFIGURED"

"""Official NSE surveillance evidence for research; never grants trading approval."""
from __future__ import annotations
import copy
import hashlib
import json
import re
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from src.ingestion import DataQualityError

MAX_BYTES = 10_000_000

def canonical_hash(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()

def source_urls(report):
    start = date.fromisoformat(report["sources"][0]["asof_date"])
    end = date.fromisoformat(report["target_date"])
    if start > end:
        raise DataQualityError("Invalid corporate-action query interval")
    return {
        "asm": "https://www.nseindia.com/api/reportASM",
        "gsm": "https://www.nseindia.com/api/reportGSM",
        "corporate_actions": "https://www.nseindia.com/api/corporates-corporateActions?" +
            urlencode({"index": "equities", "from_date": start.strftime("%d-%m-%Y"),
                       "to_date": end.strftime("%d-%m-%Y")})}

def fetch_sources(report, *, opener=urlopen):
    """Fetch the public website endpoints; no broker or trading credentials."""
    result = {}
    for label, url in source_urls(report).items():
        request = Request(url, headers={"User-Agent": "Mozilla/5.0",
                          "Accept": "application/json", "Referer": "https://www.nseindia.com/"})
        with opener(request, timeout=25) as response:
            if response.status != 200 or "application/json" not in response.headers.get("Content-Type", ""):
                raise DataQualityError("NSE JSON source unavailable")
            raw = response.read(MAX_BYTES + 1)
        if not raw or len(raw) > MAX_BYTES:
            raise DataQualityError("Invalid NSE source size")
        payload = json.loads(raw)
        result[label] = {
            "label": label, "url": url, "status": 200,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "payload_sha256": canonical_hash(payload),
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "payload": payload}
    return result

def _payload(source, expected_url):
    if not isinstance(source, dict) or source.get("url") != expected_url or source.get("status") != 200:
        raise DataQualityError("Unexpected NSE evidence source")
    if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
        raise DataQualityError("Missing raw source hash")
    payload = source.get("payload")
    if source.get("payload_sha256") != canonical_hash(payload):
        raise DataQualityError("NSE evidence payload hash mismatch")
    try:
        retrieved = datetime.fromisoformat(source["retrieved_at"])
        if retrieved.tzinfo is None:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise DataQualityError("Timezone-aware source retrieval time required") from None
    return payload, retrieved

def _source_day(value):
    if not isinstance(value, str):
        raise DataQualityError("Missing NSE source date")
    for fmt in ("%d-%b-%Y", "%d-%b-%Y %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    raise DataQualityError("Unrecognized NSE source date")

def _identity(row):
    if (not isinstance(row, dict) or not isinstance(row.get("symbol"), str)
            or not re.fullmatch(r"[A-Z0-9&._-]+", row["symbol"])
            or not isinstance(row.get("isin"), str)
            or not re.fullmatch(r"[A-Z0-9]{12}", row["isin"])):
        raise DataQualityError("Invalid NSE identity")
    return row["symbol"], row["isin"]

def audit_eligibility(report, sources):
    """Positive exchange restrictions override a clear broker flag.

    Absent matches only describe the explicitly dated lists. Effective-date,
    corporate-action completeness, calendar and order approval stay unverified.
    """
    if report.get("mode") != "LIQUIDITY_RESEARCH_ONLY" or report.get("execution_enabled") is not False:
        raise DataQualityError("Research snapshot required")
    urls = source_urls(report)
    payloads = {}
    retrievals = {}
    for label, url in urls.items():
        if label not in sources:
            raise DataQualityError("Missing required NSE evidence")
        payloads[label], retrievals[label] = _payload(sources[label], url)
    asm = payloads["asm"]
    if not isinstance(asm, dict) or set(asm) != {"longterm", "shortterm"}:
        raise DataQualityError("Unrecognized NSE ASM schema")
    lists = {}
    for label in ("longterm", "shortterm"):
        group = asm[label]
        if not isinstance(group, dict) or not isinstance(group.get("data"), list):
            raise DataQualityError("Incomplete NSE ASM lists")
        lists["ASM_" + label.upper()] = (group["data"], "asmTime", "asmSurvIndicator", "asm")
    if not isinstance(payloads["gsm"], list):
        raise DataQualityError("Unrecognized NSE GSM schema")
    lists["GSM"] = (payloads["gsm"], "gsmTime", "gsmStage", "gsm")
    restrictions = []
    dates = set()
    duplicate_counts = {}
    for category, (rows, time_key, stage_key, source_key) in lists.items():
        # An empty endpoint provides no list date; absence cannot imply clearance.
        if not rows:
            raise DataQualityError("Undated empty surveillance list")
        seen = {}
        duplicate_counts[category] = 0
        for row in rows:
            symbol, isin = _identity(row)
            source_day = _source_day(row.get(time_key))
            if source_day > retrievals[source_key].astimezone(ZoneInfo("Asia/Kolkata")).date():
                raise DataQualityError("Future-dated surveillance evidence")
            if not isinstance(row.get(stage_key), str) or not row[stage_key].strip():
                raise DataQualityError("Missing surveillance stage")
            identity = (symbol, source_day, row[stage_key])
            if isin in seen:
                if seen[isin] != identity:
                    raise DataQualityError("Conflicting NSE surveillance identity")
                duplicate_counts[category] += 1
                continue
            seen[isin] = identity
            dates.add(source_day)
            restrictions.append({"symbol": symbol, "isin": isin, "category": category,
                                 "stage": row[stage_key], "source_asof_date": source_day.isoformat()})
    expected_day = date.fromisoformat(report["asof_date"])
    source_asof_matches = dates == {expected_day}
    actions = payloads["corporate_actions"]
    if not isinstance(actions, list):
        raise DataQualityError("Unrecognized corporate-action schema")
    events = []
    seen_events = set()
    window_start = date.fromisoformat(report["sources"][0]["asof_date"])
    window_end = date.fromisoformat(report["target_date"])
    for row in actions:
        symbol, isin = _identity(row)
        ex_day = _source_day(row.get("exDate"))
        if not window_start <= ex_day <= window_end:
            raise DataQualityError("Corporate action outside requested interval")
        subject = row.get("subject")
        if not isinstance(subject, str) or not subject.strip():
            raise DataQualityError("Missing corporate-action purpose")
        identity = (symbol, isin, ex_day, subject)
        if identity in seen_events:
            raise DataQualityError("Duplicate corporate action")
        seen_events.add(identity)
        kind = ("CAPITAL_STRUCTURE_REVIEW"
                if any(x in subject.lower() for x in ("bonus", "split", "rights", "demerger",
                                                      "scheme", "amalgamation", "consolidation"))
                else "DIVIDEND" if "dividend" in subject.lower() else "OTHER_REVIEW")
        events.append({"symbol": symbol, "isin": isin, "ex_date": ex_day.isoformat(),
                       "subject": subject, "kind": kind})
    result = copy.deepcopy(report)
    for row in result["candidates"]:
        row.setdefault("pre_nse_reference_review_status", row["reference_review_status"])
        row["reference_review_status"] = row["pre_nse_reference_review_status"]
    pre_count = sum(row["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"
                    for row in result["candidates"])
    conflicts = []
    for row in result["candidates"]:
        matches = [item for item in restrictions if item["isin"] == row["isin"]
                   or item["symbol"] == row["symbol"]]
        row_events = [item for item in events if item["isin"] == row["isin"]
                      or item["symbol"] == row["symbol"]]
        conflict = any(item["isin"] != row["isin"] or item["symbol"] != row["symbol"]
                       for item in matches + row_events)
        row["nse_surveillance"] = {
            "matches": matches, "source_asof_matches_snapshot": source_asof_matches,
            "target_effective_date_verified": False}
        row["corporate_actions"] = row_events
        row["indicator_history_review_required"] = bool(row_events)
        row["corporate_action_adjustments_verified"] = False
        if conflict:
            row["reference_review_status"] = "HOLD_NSE_IDENTITY_CONFLICT"
        elif matches:
            if row["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE":
                conflicts.append(row["symbol"])
            row["reference_review_status"] = (
                "EXCLUDED_NSE_ASM" if any(x["category"].startswith("ASM") for x in matches)
                else "EXCLUDED_NSE_GSM")
        elif not source_asof_matches and row["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE":
            row["reference_review_status"] = "HOLD_SURVEILLANCE_SOURCE_DATE"
    result["summary"]["pre_nse_reference_candidate_count"] = pre_count
    result["summary"]["reference_research_candidate_count"] = sum(
        row["reference_review_status"] == "HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE"
        for row in result["candidates"])
    result["summary"]["nse_surveillance_excluded_count"] = sum(
        row["reference_review_status"] in {"EXCLUDED_NSE_ASM", "EXCLUDED_NSE_GSM"}
        for row in result["candidates"])
    result["summary"]["newly_excluded_by_nse_count"] = len(conflicts)
    result["summary"]["nse_identity_conflict_count"] = sum(
        row["reference_review_status"] == "HOLD_NSE_IDENTITY_CONFLICT"
        for row in result["candidates"])
    result["nse_eligibility_audit"] = {
        "source_asof_dates": sorted(day.isoformat() for day in dates),
        "source_asof_matches_snapshot": source_asof_matches,
        "surveillance_counts": {key: len(value[0]) for key, value in lists.items()},
        "identical_restriction_duplicates": duplicate_counts,
        "broker_clear_but_nse_restricted": conflicts,
        "source_manifests": {key: {k: v for k, v in value.items() if k != "payload"}
                             for key, value in sources.items()},
        "corporate_action_query_from": window_start.isoformat(),
        "corporate_action_query_to": window_end.isoformat(),
        "corporate_action_point_in_time_verified": False,
        "corporate_action_completeness_verified": False,
        "surveillance_target_effective_date_verified": False}
    result["tradable_count"] = 0
    result["execution_enabled"] = False
    result["restrictions_verified"] = False
    return result

"""Finite daily research-universe build from public NSE and Dhan references."""
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
import tempfile
from urllib.request import Request, urlopen
import yaml
from src.eligibility import dhan_mapping
from src.universe_research import build_research
from src.universe_reference import attach_references
from src.nse_eligibility_audit import audit_eligibility, fetch_sources

ROOT = Path(__file__).resolve().parent.parent
CALENDAR_PATH = ROOT / "config" / "research_calendar.json"
CONFIG_PATH = ROOT / "config" / "universe.yaml"
MASTER_URLS = {
    "equity.csv": "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
    "bands.csv": "https://nsearchives.nseindia.com/content/equities/sec_list.csv",
    "dhan.csv": "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"}

def reference_dates_for(target_date, calendar):
    target = date.fromisoformat(target_date)
    if target.isoformat() != target_date:
        raise ValueError("Canonical target date required")
    if calendar.get("mode") != "BOUNDED_RESEARCH_CALENDAR":
        raise ValueError("Reviewed research calendar required")
    earliest, latest = map(date.fromisoformat, (calendar["earliest_target"], calendar["latest_target"]))
    if not earliest <= target <= latest:
        raise ValueError("CALENDAR_REVIEW_REQUIRED")
    sessions = calendar["sessions"]
    parsed = [date.fromisoformat(day) for day in sessions]
    if any(day.isoformat() != text for day, text in zip(parsed, sessions)) or parsed != sorted(set(parsed)):
        raise ValueError("Invalid research session dates")
    if target_date not in sessions:
        raise ValueError("TARGET_NOT_RESEARCH_SESSION")
    index = sessions.index(target_date)
    previous = sessions[max(0, index-20):index]
    if len(previous) != 20:
        raise ValueError("Twenty previous sessions required")
    return previous

def download_public(url, path, *, maximum, opener=urlopen):
    digest = hashlib.sha256()
    size = 0
    with opener(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25) as response:
        if response.status != 200:
            raise ValueError("Public source unavailable")
        with Path(path).open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > maximum:
                    raise ValueError("Public source too large")
                digest.update(chunk)
                handle.write(chunk)
    if not size:
        raise ValueError("Empty public source")
    return {"url": url, "sha256": digest.hexdigest(), "bytes": size}

def build_daily_universe(target_date, *, calendar_path=CALENDAR_PATH, config_path=CONFIG_PATH,
                         download=download_public, nse_fetch=fetch_sources):
    calendar_bytes = Path(calendar_path).read_bytes()
    config_bytes = Path(config_path).read_bytes()
    calendar = json.loads(calendar_bytes)
    dates = reference_dates_for(target_date, calendar)
    cfg = yaml.safe_load(config_bytes)
    manifests = []
    with tempfile.TemporaryDirectory(prefix="universe_refresh_") as directory:
        root = Path(directory)
        paths = []
        for day in dates:
            filename = "BhavCopy_NSE_CM_0_0_0_" + day.replace("-", "") + "_F_0000.csv.zip"
            url = "https://nsearchives.nseindia.com/content/cm/" + filename
            path = root / filename
            manifest = download(url, path, maximum=12_000_000)
            manifest["asof_date"] = day
            manifests.append(manifest)
            paths.append((day, path))
        master_paths = {}
        for filename, url in MASTER_URLS.items():
            path = root / filename
            manifests.append(download(url, path, maximum=100_000_000 if filename == "dhan.csv" else 12_000_000))
            master_paths[filename] = path
        mapping = dhan_mapping(master_paths["dhan.csv"])
        report = build_research(paths, target_date, cfg, mapping)
        report = attach_references(report, master_paths["equity.csv"],
                                   master_paths["bands.csv"], master_paths["dhan.csv"])
        nse = nse_fetch(report)
        report = audit_eligibility(report, nse)
        if report["nse_eligibility_audit"]["source_asof_matches_snapshot"] is not True:
            raise ValueError("NSE_SURVEILLANCE_SOURCE_DATE_MISMATCH")
        for source in report["sources"]:
            source["url"] = next(item["url"] for item in manifests if item.get("asof_date") == source["asof_date"])
        report["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
        report["refresh"] = {
            "mode": "AUTOMATED_RESEARCH_BUILD", "built_at": datetime.now(timezone.utc).isoformat(),
            "calendar_sha256": hashlib.sha256(calendar_bytes).hexdigest(),
            "calendar_review_through": calendar["latest_target"],
            "target_eligibility_verified": False}
        evidence = {"nse": nse, "calendar": calendar,
                    "config_sha256": report["config_sha256"], "public_sources": manifests}
        return report, evidence

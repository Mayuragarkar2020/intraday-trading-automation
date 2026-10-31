"""Regression tests for atomic NSE archive caching (no network access)."""
import io
import zipfile
from pathlib import Path

import pytest

from scripts import download_20_sessions as downloader


def _dates_file(tmp_path):
    dates = [f"2026-09-{day:02d}" for day in range(1, 21)]
    path = tmp_path / "dates.txt"
    path.write_text("\n".join(dates))
    return path, dates


def _archive(day):
    csv = (
        "TckrSymb,SctySrs,ISIN,TradDt,ClsPric,TtlTradgVol,TtlTrfVal\n"
        f"TEST,EQ,INE000A01001,{day},500,100,50000\n"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("daily.csv", csv)
    return buffer.getvalue()


class _Response:
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.data[:size]


def test_failed_download_does_not_publish_archive(tmp_path, monkeypatch):
    dates_file, days = _dates_file(tmp_path)
    monkeypatch.setattr(downloader.urllib.request, "urlopen", lambda *a, **k: _Response(b"x" * 1500))
    with pytest.raises(Exception):
        downloader.download(dates_file, tmp_path / "raw")
    assert not list((tmp_path / "raw").glob("*.zip"))
    assert not list((tmp_path / "raw").glob(".nse-*"))


def test_valid_download_is_cached_and_manifest_uses_final_filename(tmp_path, monkeypatch):
    dates_file, days = _dates_file(tmp_path)
    monkeypatch.setattr(downloader.urllib.request, "urlopen", lambda request, **kw: _Response(
        _archive(next(day for day in days if day.replace("-", "") in request.full_url))
    ))
    monkeypatch.setattr(downloader.time, "sleep", lambda _: None)
    manifests = downloader.download(dates_file, tmp_path / "raw")
    assert len(manifests) == 20
    assert all(Path(m["filename"]).suffix == ".zip" for m in manifests)
    assert len(list((tmp_path / "raw").glob("*.zip"))) == 20
    assert not list((tmp_path / "raw").glob(".nse-*"))


def test_corrupt_cached_archive_is_rejected_without_network(tmp_path, monkeypatch):
    dates_file, days = _dates_file(tmp_path)
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / f"BhavCopy_NSE_CM_0_0_0_{days[0].replace('-', '')}_F_0000.csv.zip").write_bytes(b"invalid")
    monkeypatch.setattr(downloader.urllib.request, "urlopen", lambda *a, **kw: pytest.fail("network called"))
    with pytest.raises(Exception):
        downloader.download(dates_file, raw)

import csv
import zipfile
from pathlib import Path
import pytest
from src.ingestion import DataQualityError, load_bhavcopy

HEADER = ["TckrSymb","SctySrs","ISIN","TradDt","ClsPric","TtlTradgVol","TtlTrfVal"]
ROW = ["ABC","EQ","INE000A01000","2026-10-30","1000","1000000","1000000000"]

def write_csv(p: Path, row=ROW, header=HEADER):
    with p.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerow(row)

def test_load_valid_csv(tmp_path):
    p = tmp_path / "bhav.csv"; write_csv(p)
    rows, manifest = load_bhavcopy(p, "2026-10-30")
    assert rows[0]["volume"] == 1000000
    assert rows[0]["turnover_inr"] == 1000000000
    assert len(manifest["sha256"]) == 64

def test_zip_valid(tmp_path):
    p = tmp_path / "bhav.csv"; write_csv(p)
    z = tmp_path / "bhav.zip"
    with zipfile.ZipFile(z, "w") as a: a.write(p, arcname=p.name)
    assert len(load_bhavcopy(z, "2026-10-30")[0]) == 1

def test_missing_column_fails(tmp_path):
    p = tmp_path / "bhav.csv"; write_csv(p, header=HEADER[:-1])
    with pytest.raises(DataQualityError):
        load_bhavcopy(p, "2026-10-30")

def test_future_date_fails(tmp_path):
    p = tmp_path / "bhav.csv"; write_csv(p)
    with pytest.raises(DataQualityError, match="Date mismatch"):
        load_bhavcopy(p, "2026-10-29")

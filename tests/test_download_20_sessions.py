import csv
import io
import zipfile
from datetime import date, timedelta
from pathlib import Path
import pytest
from scripts.download_20_sessions import download

def test_download_validates_cached_official_style_archives(tmp_path):
    days=[(date(2026,9,1)+timedelta(days=i)).isoformat() for i in range(20)]
    dates=tmp_path/"dates.txt";dates.write_text("\n".join(days))
    out=tmp_path/"archive";out.mkdir()
    for day in days:
        content=io.StringIO()
        writer=csv.writer(content)
        writer.writerow(["TckrSymb","SctySrs","ISIN","TradDt","ClsPric","TtlTradgVol","TtlTrfVal"])
        writer.writerow(["ABC","EQ","INE000A01000",day,"1000","1000000","1000000000"])
        name="BhavCopy_NSE_CM_0_0_0_"+day.replace("-","")+"_F_0000.csv.zip"
        with zipfile.ZipFile(out/name,"w") as z:
            z.writestr("stock.csv",content.getvalue())
    manifest=download(dates,out)
    assert len(manifest)==20
    assert all(m["eq_rows"]==1 for m in manifest)

def test_does_not_accept_incomplete_session_calendar(tmp_path):
    p=tmp_path/"dates.txt";p.write_text("2026-09-01\n")
    with pytest.raises(ValueError):
        download(p,tmp_path/"archive")

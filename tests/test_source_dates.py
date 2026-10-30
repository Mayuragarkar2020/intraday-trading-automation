from src.source_dates import report_names
def test_historical_verified_filenames():
    n=report_names("2026-09-25","2026-09-26")
    assert n["price_band_complete"]=="sec_list_25092026.csv"
    assert n["price_band_changes"]=="eq_band_changes_25092026.csv"
    assert n["surveillance"]=="REG_IND250926.csv"
    assert n["fo_bhavcopy"].endswith("20260925_F_0000.csv.zip")

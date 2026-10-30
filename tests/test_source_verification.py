from src.source_verification import REQUIRED_DHAN, DHAN_DETAILED_URL

def test_required_detailed_master_columns():
    assert REQUIRED_DHAN == {"EXCH_ID", "SEGMENT", "ISIN", "SERIES", "SECURITY_ID"}

def test_download_uses_documented_https_source():
    assert DHAN_DETAILED_URL.startswith("https://images.dhan.co/")

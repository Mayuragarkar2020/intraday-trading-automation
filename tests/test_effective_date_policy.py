from src.effective_date_policy import validate_manifest,REQUIRED

def test_missing_evidence_holds():
    r=validate_manifest({"asof_date":"2026-10-30","target_date":"2026-11-02","sources":{}},"2026-10-30","2026-11-02")
    assert not r["source_evidence_complete"]
    assert all(x=="HOLD_NO_SOURCE_EVIDENCE" for x in r["decisions"].values())

def test_reviewed_evidence_is_research_only():
    sources={k:{"source_session":"2026-10-30","effective_for_session":"2026-11-02",
                "evidence_reviewed":True,"sha256":"a"*64} for k in REQUIRED}
    r=validate_manifest({"asof_date":"2026-10-30","target_date":"2026-11-02","sources":sources},"2026-10-30","2026-11-02")
    assert r["source_evidence_complete"]
    assert not r["may_place_orders"]

def test_stale_effective_date_holds():
    sources={k:{"source_session":"2026-10-30","effective_for_session":"2026-10-30",
                "evidence_reviewed":True,"sha256":"a"*64} for k in REQUIRED}
    r=validate_manifest({"asof_date":"2026-10-30","target_date":"2026-11-02","sources":sources},"2026-10-30","2026-11-02")
    assert not r["source_evidence_complete"]
    assert all(x=="HOLD_EFFECTIVE_DATE_UNVERIFIED" for x in r["decisions"].values())

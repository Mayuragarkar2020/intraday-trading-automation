from src.source_readiness import evaluate_readiness,required_sources

def test_missing_required_file_blocks_readiness():
    def checker(url):
        return {"state":"UNAVAILABLE"} if "sec_list_" in url else {"state":"AVAILABLE"}
    result=evaluate_readiness("2026-10-30","2026-10-30",checker=checker)
    assert result["status"]=="NOT_READY"
    assert not result["may_publish_trading_universe"]

def test_all_sources_still_research_only():
    result=evaluate_readiness("2026-09-25","2026-09-25",
                              checker=lambda url:{"state":"AVAILABLE"})
    assert result["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY"
    assert result["may_publish_trading_universe"] is False
    assert len(required_sources("2026-09-25","2026-09-25"))==5

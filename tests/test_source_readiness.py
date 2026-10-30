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

from src.source_readiness import retry_readiness

def test_retry_then_ready_remains_research_only():
    calls={"n":0}
    def checker(url):
        calls["n"]+=1
        return {"state":"UNAVAILABLE"} if calls["n"]<=5 else {"state":"AVAILABLE"}
    result=retry_readiness("2026-10-30","2026-10-30",attempts=3,delay_seconds=0,checker=checker,sleep=lambda _:None)
    assert result["attempts_used"]==2
    assert result["status"]=="SOURCES_AVAILABLE_RESEARCH_ONLY"
    assert result["may_publish_trading_universe"] is False

def test_exhausted_retries_do_not_approve():
    r=retry_readiness("2026-10-30","2026-10-30",attempts=2,delay_seconds=0,
                       checker=lambda _:{"state":"UNAVAILABLE","http_status":404},
                       sleep=lambda _:None)
    assert r["status"]=="NOT_READY"
    assert r["attempts_used"]==2
    assert r["attempt_history"][-1]["http_codes"]

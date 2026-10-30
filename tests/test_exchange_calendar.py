import pytest
from datetime import date
from src.exchange_calendar import regular_session,next_regular_session,check_target
def test_october_to_november():
    assert next_regular_session("2026-10-30")=="2026-11-02"
    assert check_target("2026-10-30","2026-11-02")["approval_state"]=="RESEARCH_ONLY_NO_TRADING"
def test_holidays_and_weekends():
    assert not regular_session(date(2026,11,10))
    assert next_regular_session("2026-11-09")=="2026-11-11"
    assert not regular_session(date(2026,10,31))
def test_wrong_target_fails():
    with pytest.raises(ValueError):check_target("2026-10-30","2026-11-03")
def test_unreviewed_year_fails():
    with pytest.raises(ValueError):next_regular_session("2026-12-31")

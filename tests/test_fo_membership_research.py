from scripts.fo_membership_research import assess

def test_same_date_membership_classifies_only_unclassified_stocks():
    bands={"approval_state":"RESEARCH_ONLY_NO_TRADING","rows":[
        {"symbol":"ABC","isin":"INE000A01000","band_result":"HOLD_FO_MEMBERSHIP_UNVERIFIED"},
        {"symbol":"XYZ","isin":"INE000B01000","band_result":"HOLD_FO_MEMBERSHIP_UNVERIFIED"},
        {"symbol":"OTHER","isin":"INE000C01000","band_result":"BAND_SCREEN_PASSED"}]}
    result=assess(bands,{"ABC"})
    assert result["counts"]=={"DYNAMIC_BAND_FO_RESEARCH_ONLY":1,"HOLD_NO_BAND_NOT_IN_FO":1}
    assert result["approval_state"]=="RESEARCH_ONLY_NO_TRADING"

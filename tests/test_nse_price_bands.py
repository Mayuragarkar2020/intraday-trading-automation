import csv
from src.nse_price_bands import parse_complete, parse_changes, classify

def test_bands_with_effective_next_day_override(tmp_path):
    full=tmp_path/"full.csv"
    full.write_text("Symbol,Series,Security Name,Band,Remarks\nABC,EQ,ABC LTD,10,-\nXYZ,EQ,XYZ LTD,5,-\n")
    delta=tmp_path/"change.csv"
    delta.write_text("Sr. No,Symbol,Series,Security Name,From,To\n1,ABC,EQ,ABC LTD,10,5\n")
    complete=parse_complete(full)
    changes=parse_changes(delta)
    assert classify("ABC",complete,changes)=="EXCLUDED_NARROW_BAND"
    assert classify("XYZ",complete,changes)=="EXCLUDED_NARROW_BAND"
    assert classify("MISSING",complete,changes)=="HOLD_BAND_NOT_LISTED"

def test_disagreeing_change_record_is_held(tmp_path):
    full=tmp_path/"full.csv"
    full.write_text("Symbol,Series,Security Name,Band,Remarks\nABC,EQ,ABC LTD,10,-\n")
    delta=tmp_path/"change.csv"
    delta.write_text("Sr. No,Symbol,Series,Security Name,From,To\n1,ABC,EQ,ABC LTD,20,5\n")
    assert classify("ABC",parse_complete(full),parse_changes(delta))=="HOLD_INCONSISTENT_BAND"

def test_no_band_is_held_for_separate_validation(tmp_path):
    p=tmp_path/'bands.csv'
    p.write_text('Symbol,Series,Security Name,Band,Remarks\nABC,EQ,ABC LTD,No Band,-\n')
    assert classify('ABC',parse_complete(p),{})=='HOLD_FO_MEMBERSHIP_UNVERIFIED'

def test_no_band_requires_date_consistent_fo_membership(tmp_path):
    p=tmp_path/"bands.csv"
    p.write_text("Symbol,Series,Security Name,Band,Remarks\nABC,EQ,ABC LTD,No Band,-\n")
    bands=parse_complete(p)
    assert classify("ABC",bands,{"ABC":(None,None)},{"ABC"})=="DYNAMIC_BAND_FO_RESEARCH_ONLY"
    assert classify("ABC",bands,{},set())=="HOLD_FO_MEMBERSHIP_UNVERIFIED"

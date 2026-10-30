from src.nse_surveillance import load_surveillance,classify
def test_basic_clear_and_unknown_codes_hold(tmp_path):
    p=tmp_path/"reg.csv"
    p.write_text("Symbol,Series,Status,GSM,Long_Term_Additional_Surveillance_Measure (Long Term ASM),Short_Term_Additional_Surveillance_Measure (Short Term ASM)\nABC,EQ,A,100,100,100\nXYZ,EQ,A,1,100,100\n")
    r=load_surveillance(p)
    assert classify("ABC",r)=="SURVEILLANCE_BASIC_CLEAR"
    assert classify("XYZ",r)=="HOLD_SURVEILLANCE_FLAG_REVIEW"
    assert classify("MISSING",r)=="HOLD_SURVEILLANCE_NOT_FOUND"

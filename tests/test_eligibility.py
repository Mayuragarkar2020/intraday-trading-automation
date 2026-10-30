from src.eligibility import reconcile

def test_no_mapping_is_hold():
    rows=[{"isin":"INE000A01000","liquidity_pass":True}]
    assert reconcile(rows,{}, {})[0]["status"]=="HOLD_DHAN_MAPPING"

def test_no_restrictions_is_hold():
    rows=[{"isin":"INE000A01000","liquidity_pass":True}]
    assert reconcile(rows,{"INE000A01000":["10"]},{})[0]["status"]=="HOLD_RESTRICTIONS"

def test_multiple_mapping_is_hold():
    rows=[{"isin":"INE000A01000","liquidity_pass":True}]
    assert reconcile(rows,{"INE000A01000":["10","11"]},{"INE000A01000":{"approved":True,"reason":""}})[0]["status"]=="HOLD_DHAN_MAPPING"

def test_manual_approval_not_equivalent_to_production_verification():
    rows=[{"isin":"INE000A01000","liquidity_pass":True}]
    x=reconcile(rows,{"INE000A01000":["10"]},{"INE000A01000":{"approved":True,"reason":"Reviewed"}})
    assert x[0]["status"]=="ELIGIBLE_MANUALLY_REVIEWED"

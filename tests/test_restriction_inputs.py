import csv
from src.restriction_inputs import read_control, combine_controls, ControlError
import pytest
I="INE000A01000"

def test_missing_control_fails_closed():
    assert combine_controls([I],[{I:{"action":"ALLOW"}},{}])[I]["action"]=="HOLD"

def test_all_independent_controls_required():
    a={I:{"action":"ALLOW"}}
    assert combine_controls([I],[a,a])[I]["approved"]
    assert combine_controls([I],[a,{I:{"action":"BLOCK"}}])[I]["action"]=="BLOCK"

def test_stale_approval_is_not_reused(tmp_path):
    p=tmp_path/"control.csv"
    with p.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["isin","target_date","action","reason"])
        w.writerow([I,"2026-10-29","ALLOW",""])
    rows,meta=read_control(p,"2026-10-30")
    assert rows=={}
    assert meta["records"]==0

def test_duplicate_fails(tmp_path):
    p=tmp_path/"control.csv"
    with p.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["isin","target_date","action","reason"])
        w.writerow([I,"2026-10-30","ALLOW",""])
        w.writerow([I,"2026-10-30","BLOCK","restricted"])
    with pytest.raises(ControlError):
        read_control(p,"2026-10-30")

"""Versioned synthetic fault cases, never market evidence or strategy returns."""
from copy import deepcopy
from datetime import datetime
from src.paper_engine import replay
from src.paper_models import ReplayRequest

def example_request():
    def bar(at, opening, high, low, close, ema=499, **faults):
        return dict(time="2026-10-30T"+at+":00+05:30",open=opening,high=high,
                    low=low,close=close,ema10=ema,volume=100000,**faults)
    return {"label":"Synthetic EMA exit example","source":"SYNTHETIC",
        "round_trip_cost_per_share":"0.50","slippage_bps":"5","participation_pct":"1",
        "plans":[{"plan_id":"example","symbol":"EXAMPLE","known_at":"2026-10-30T09:45:00+05:30",
            "trigger":"500","stop":"490","reference_status":"RESEARCH_ONLY","price_band":20,
            "bars":[bar("09:50",499,505,495,503),bar("09:55",503,519,501,518),
                    bar("10:00",518,519,510,511,512),bar("10:05",511,513,508,510)]}]}

def scenario_suite():
    cases=[]
    def add(name, mutate, check):
        value=deepcopy(example_request());mutate(value);cases.append((name,value,check))
    def plan(value):return value["plans"][0]
    def event(kind):return lambda r:any(e["kind"]==kind for e in r["events"])
    add("EMA exit fills on the following bar",lambda v:None,lambda r:r["trades"][0]["exit_bar_close"].endswith("10:05:00+05:30") and r["trades"][0]["exit_reason"]=="EMA10_CLOSE")
    add("5% band is rejected",lambda v:plan(v).update(price_band=5),lambda r:r["summary"]["entries"]==0 and r["orders"][0]["reason"]=="LOW_PRICE_BAND")
    add("Identity hold is rejected",lambda v:plan(v).update(reference_status="HOLD"),lambda r:r["summary"]["entries"]==0)
    add("Entry rejection creates no position",lambda v:plan(v)["bars"][0].update(reject_entry=True),lambda r:r["summary"]["entries"]==0)
    add("Zero liquidity cannot create a fill",lambda v:[b.update(volume=0) for b in plan(v)["bars"]],lambda r:r["summary"]["entries"]==0)
    add("Entry partial fill cancels its remainder",lambda v:plan(v)["bars"][0].update(volume=100),event("ENTRY_REMAINDER_CANCELLED"))
    add("Rejected stop change keeps original stop",lambda v:plan(v)["bars"][1].update(reject_stop_change=True),event("STOP_CHANGE_REJECTED"))
    add("Unfillable exit remains unresolved",lambda v:[b.update(can_fill=False) for b in plan(v)["bars"][1:]],lambda r:r["summary"]["open_positions"]==1 and not r["summary"]["complete"])
    add("Ambiguous entry and stop is invalidated",lambda v:plan(v)["bars"][0].update(low=489),lambda r:r["summary"]["entries"]==0)
    add("Gap through stop uses adverse opening price",lambda v:plan(v)["bars"][1].update(open=480,high=485,low=475,close=480),lambda r:r["trades"][0]["exit_reason"]=="STOP" and float(r["trades"][0]["exit_average"])<480)
    def second(v):
        other=deepcopy(plan(v));other.update(plan_id="second",symbol="SECOND");v["plans"].append(other)
    add("Competing signals cannot exceed daily trade limit",second,lambda r:r["summary"]["entries"]==1 and r["orders"][1]["reason"]=="DAILY_TRADE_LIMIT")
    add("Missing bar blocks replay",lambda v:plan(v)["bars"].pop(1),"error")
    add("Duplicate bar blocks replay",lambda v:plan(v)["bars"].insert(1,deepcopy(plan(v)["bars"][0])),"error")
    add("Future data blocks replay",lambda v:None,"future")
    rows=[]
    for name,value,check in cases:
        try:
            result=replay(ReplayRequest.model_validate(value),as_of=datetime.fromisoformat("2026-10-30T09:45:00+05:30") if check=="future" else datetime.fromisoformat("2026-10-31T12:00:00+05:30"))
            passed=False if isinstance(check,str) else bool(check(result))
            rows.append({"name":name,"passed":passed,"result":result["summary"],"run_id":result["run_id"]})
        except ValueError as error:
            rows.append({"name":name,"passed":check in ("error","future"),"detail":str(error)})
    return {"mode":"SYNTHETIC_SCENARIO_SUITE","execution_enabled":False,"live":False,
        "passed":sum(r["passed"] for r in rows),"total":len(rows),"scenarios":rows,
        "example":example_request(),"warning":"Controlled software checks only. These are not historical trading results."}

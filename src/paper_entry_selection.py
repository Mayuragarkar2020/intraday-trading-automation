"""Inactive paper-entry ranking and prospective ledger reservations.

No feed/API/cron imports this module. Source-verification attestations must
come from a future trusted adapter, never from uploaded diagnostic inputs.
This library does not independently certify those attestations or fill orders.
"""
from datetime import timedelta,time
from decimal import Decimal,ROUND_FLOOR
import hashlib
from typing import Literal

from pydantic import BaseModel,ConfigDict,Field,model_validator

from src.forward_paper_ledger import CAPITAL,amount,encode,initial_state,instant
from src.risk_engine import RiskPolicy,size_long

POLICY = "LIQUIDITY_20D_V1"


class Strict(BaseModel):
    model_config=ConfigDict(extra="forbid",allow_inf_nan=False)


class BreakoutCandidate(Strict):
    symbol:str=Field(pattern=r"^[A-Z0-9&._-]{2,30}$")
    security_id:str=Field(pattern=r"^[0-9]{1,12}$")
    signal_id:str=Field(pattern=r"^[a-f0-9]{64}$")
    source_sha256:str=Field(pattern=r"^[a-f0-9]{64}$")
    universe_revision:str=Field(pattern=r"^[a-f0-9]{64}$")
    status:Literal["BREAKOUT_CONFIRMED"]
    setup_known_at:str
    breakout_observed_at:str
    avg_turnover_20d_cr:Decimal=Field(gt=0,le=1000000000,max_digits=30,decimal_places=18)
    entry_limit:Decimal=Field(ge=300,le=5000,max_digits=16,decimal_places=6)
    initial_stop:Decimal=Field(gt=0,le=5000,max_digits=16,decimal_places=6)
    evidence_kind:Literal["TICK_RECEIPT","COMPLETED_BAR_RECEIPT"]="TICK_RECEIPT"
    setup_receipt_id:str|None=Field(default=None,pattern=r"^[a-f0-9]{64}$")
    breakout_receipt_id:str|None=Field(default=None,pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def valid_prices(self):
        if self.initial_stop>=self.entry_limit: raise ValueError("Stop must be below entry limit")
        if instant(self.setup_known_at)>=instant(self.breakout_observed_at):
            raise ValueError("Setup must be known before breakout observation")
        if (self.setup_receipt_id is None)!=(self.breakout_receipt_id is None):
            raise ValueError("Both receipt identities required")
        if self.setup_receipt_id is not None:
            if (self.evidence_kind!="COMPLETED_BAR_RECEIPT" or self.signal_id!=
                    hashlib.sha256(encode([self.setup_receipt_id,self.breakout_receipt_id]).encode()).hexdigest()):
                raise ValueError("Signal must bind both receipt identities")
        return self


class EntryBatch(Strict):
    batch_id:str=Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    interval_start:str
    decision_at:str
    round_trip_cost_per_share:Decimal=Field(ge=0,le=10000,max_digits=16,decimal_places=6)
    candidates:list[BreakoutCandidate]=Field(min_length=1,max_length=120)
    # These are required trusted-adapter attestations, not proof of verification.
    timestamp_verified:bool=False
    session_contract_verified:bool=False
    reference_prices_verified:bool=False
    breakout_receipts_verified:bool=False

    @model_validator(mode="after")
    def valid_batch(self):
        start,decision=instant(self.interval_start),instant(self.decision_at)
        if (start.second or start.microsecond or start.minute%5 or
                not time(9,45)<=start.time()<time(11,30) or
                decision<start+timedelta(minutes=5) or decision.date()!=start.date()):
            raise ValueError("Completed same-session five-minute decision batch required")
        if decision-(start+timedelta(minutes=5))>timedelta(seconds=90):
            raise ValueError("Decision batch is stale")
        if len({c.symbol for c in self.candidates})!=len(self.candidates) or len({c.security_id for c in self.candidates})!=len(self.candidates):
            raise ValueError("Duplicate instrument identity")
        if len({c.signal_id for c in self.candidates})!=len(self.candidates) or len({c.universe_revision for c in self.candidates})!=1:
            raise ValueError("Signal or reference identity mismatch")
        for candidate in self.candidates:
            known,seen=instant(candidate.setup_known_at),instant(candidate.breakout_observed_at)
            valid_seen=(start<=seen<start+timedelta(minutes=5) if candidate.evidence_kind=="TICK_RECEIPT"
                        else start+timedelta(minutes=5)<=seen<=decision)
            if (not valid_seen or known.date()!=start.date() or
                    candidate.evidence_kind=="COMPLETED_BAR_RECEIPT" and known>=start):
                raise ValueError("Breakout belongs to a different interval/session")
        return self


def canonical_batch(batch):
    data=batch.model_dump(mode="json")
    data["interval_start"]=instant(batch.interval_start).isoformat()
    data["decision_at"]=instant(batch.decision_at).isoformat()
    data["round_trip_cost_per_share"]=format(batch.round_trip_cost_per_share.normalize(),"f")
    for row in data["candidates"]:
        for key in ("setup_receipt_id","breakout_receipt_id"):
            if row[key] is None: row.pop(key)
        if row["evidence_kind"]=="TICK_RECEIPT":
            row.pop("evidence_kind")  # retain fingerprints of existing v1 reservations
        for field in ("avg_turnover_20d_cr","entry_limit","initial_stop"):
            row[field]=format(Decimal(row[field]).normalize(),"f")
        for field in ("setup_known_at","breakout_observed_at"):
            row[field]=instant(row[field]).isoformat()
    data["candidates"].sort(key=lambda row:(row["symbol"],row["security_id"]))
    return data


def ranked_candidates(batch):
    """Replace this policy in a future reviewed version, not the accounting."""
    return sorted(batch.candidates,key=lambda c:(-c.avg_turnover_20d_cr,c.symbol,c.security_id))


def reserve_paper_entry(ledger,account_id,batch):
    """Reserve one future paper entry; selection evidence commits with the order.

    All current research streams are unverified and must hold here. No fill,
    runtime enablement, or earlier bar-open timestamp is invented by selection.
    """
    if not isinstance(batch,EntryBatch): batch=EntryBatch.model_validate(batch)
    ranked=ranked_candidates(batch)
    ranking=[{"symbol":c.symbol,"security_id":c.security_id,"signal_id":c.signal_id,
              "avg_turnover_20d_cr":format(c.avg_turnover_20d_cr.normalize(),"f"),
              **({"setup_receipt_id":c.setup_receipt_id,"breakout_receipt_id":c.breakout_receipt_id}
                 if c.setup_receipt_id is not None else {})} for c in ranked]
    def held(reason): return {"status":reason,"ranking_policy":POLICY,"ranking":ranking,
        "execution_enabled":False,"paper_runtime_enabled":False}
    if not all((batch.timestamp_verified,batch.session_contract_verified,
                batch.reference_prices_verified,batch.breakout_receipts_verified)):
        return held("HELD_SOURCE_VERIFICATION")
    fingerprint=hashlib.sha256(encode([POLICY,canonical_batch(batch)]).encode()).hexdigest()
    event_id="selection_"+hashlib.sha256(encode([account_id,batch.batch_id]).encode()).hexdigest()
    ledger.initialize()
    def previous_result():
        old=ledger.event(account_id,event_id)
        if old:
            if old["command"].get("selection",{}).get("batch_fingerprint")!=fingerprint:
                raise ValueError("Immutable selection batch conflict")
            return {"status":"ALREADY_RESERVED","command":old["command"],
                    "execution_enabled":False,"paper_runtime_enabled":False}
        return None
    old=previous_result()
    if old: return old
    state=ledger.read(account_id) or initial_state()
    day=instant(batch.decision_at).date().isoformat()
    if (state["position"] or any(o["status"]=="PENDING" for o in state["orders"].values())
            or day in state["used_entry_dates"]):
        return previous_result() or held("HELD_ACCOUNT_ENTRY_LIMIT")
    cash=Decimal(state["cash"])
    if cash<=0: return held("HELD_INSUFFICIENT_CASH")
    if instant(batch.decision_at).time()>=time(11,30): return held("HELD_ENTRY_WINDOW_CLOSED")
    rejected=[]
    for winner in ranked:
        # Include estimated costs in both planned risk and cash affordability.
        sizing=size_long(winner.entry_limit,winner.initial_stop,batch.round_trip_cost_per_share,
            policy=RiskPolicy(capital=min(CAPITAL,cash)))
        affordable=int((cash/(winner.entry_limit+batch.round_trip_cost_per_share)).to_integral_value(rounding=ROUND_FLOOR))
        quantity=min(sizing.quantity,affordable)
        if quantity<=0:
            rejected.append({"symbol":winner.symbol,"reason":"NO_AFFORDABLE_RISK_QUANTITY"})
            continue
        selection={"policy":POLICY,"batch_id":batch.batch_id,"batch_fingerprint":fingerprint,
            "decision_at":instant(batch.decision_at).isoformat(),"ranking":ranking,"rejected":rejected,
            "source_attestations":{k:getattr(batch,k) for k in ("timestamp_verified","session_contract_verified",
                "reference_prices_verified","breakout_receipts_verified")},
            "round_trip_cost_per_share":format(batch.round_trip_cost_per_share.normalize(),"f")}
        command={"kind":"ENTRY_REQUEST","at":instant(batch.decision_at).isoformat(),
            "order_id":event_id,"signal_id":winner.signal_id,"universe_revision":winner.universe_revision,
            "source_sha256":winner.source_sha256,"known_at":instant(batch.decision_at).isoformat(),
            "quantity":quantity,"limit":amount(winner.entry_limit),"stop":amount(winner.initial_stop),
            "fee_budget":amount(quantity*batch.round_trip_cost_per_share),"symbol":winner.symbol,
            "security_id":winner.security_id,"selection":selection}
        try:
            result=ledger.apply(account_id,event_id,command)
        except ValueError:
            # Another worker may have committed a daily reservation after our read.
            old=previous_result()
            if old: return old
            current=ledger.read(account_id)
            if current and (current["position"] or any(o["status"]=="PENDING" for o in current["orders"].values())
                            or day in current["used_entry_dates"]):
                return held("HELD_ACCOUNT_ENTRY_LIMIT")
            raise
        return {"status":"RESERVED" if result["status"]=="APPLIED" else "ALREADY_RESERVED", "command":command,
                "execution_enabled":False,"paper_runtime_enabled":False}
    return held("HELD_INSUFFICIENT_CASH_OR_RISK")

"""Validated read-only candle dataset ingestion for the cockpit."""
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from src.candle_pipeline import Candle
from src.qualified_scanner import qualify

class CandleInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    time:str
    open:Decimal=Field(gt=0)
    high:Decimal=Field(gt=0)
    low:Decimal=Field(gt=0)
    close:Decimal=Field(gt=0)
    volume:int=Field(ge=0)

    def as_candle(self):
        return Candle(self.time,self.open,self.high,self.low,self.close,self.volume)

class CandidateInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    symbol:str=Field(pattern=r"^[A-Z0-9&._-]{2,30}$")
    completed_5m:list[CandleInput]=Field(min_length=3,max_length=75)
    previous_sessions:list[list[CandleInput]]=Field(min_length=20,max_length=30)
    completed_15m:list[CandleInput]=Field(min_length=21,max_length=250)
    ema_warmup_closes:list[Decimal]=Field(min_length=20,max_length=500)

class BatchInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    candidates:list[CandidateInput]=Field(min_length=1,max_length=120)

def scan_batch(batch:BatchInput):
    out=[]
    for candidate in batch.candidates:
        signal=qualify(
            [x.as_candle() for x in candidate.completed_5m],
            [[x.as_candle() for x in session] for session in candidate.previous_sessions],
            [x.as_candle() for x in candidate.completed_15m],
            candidate.ema_warmup_closes
        )
        out.append({"symbol":candidate.symbol,"mode":"USER_SUPPLIED_CANDLES",
           "status":signal.status,"reason":signal.reason,
           "entry":str(signal.trigger) if signal.trigger is not None else None,
           "stop":str(signal.initial_stop) if signal.initial_stop is not None else None,
           "range_high":str(signal.range_high) if signal.range_high is not None else None,
           "range_low":str(signal.range_low) if signal.range_low is not None else None})
    return out

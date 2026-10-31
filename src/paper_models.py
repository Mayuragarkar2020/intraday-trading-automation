"""Bounded replay input. Values describe a simulation, never exchange clearance."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

class ReplayBar(StrictModel):
    time: str
    open: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    high: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    low: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    close: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    volume: int = Field(ge=0, strict=True)
    ema10: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    can_fill: bool = True
    reject_entry: bool = False
    reject_exit: bool = False
    reject_stop_change: bool = False

class ReplayPlan(StrictModel):
    plan_id: str = Field(pattern=r"^[A-Za-z0-9_-]{1,40}$")
    symbol: str = Field(pattern=r"^[A-Z0-9&._-]{2,30}$")
    known_at: str
    trigger: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    stop: Decimal = Field(gt=0, le=10000000, max_digits=16, decimal_places=6)
    tick_size: Decimal = Field(default=Decimal("0.05"), ge=Decimal("0.0001"), le=10, decimal_places=4)
    reference_status: Literal["RESEARCH_ONLY", "HOLD", "EXCLUDED", "UNKNOWN"]
    price_band: Literal[0, 2, 5, 10, 20]  # 0 explicitly means no fixed band.
    bars: list[ReplayBar] = Field(min_length=1, max_length=75)

class ReplayRequest(StrictModel):
    label: str = Field(min_length=1, max_length=80)
    source: Literal["SYNTHETIC", "USER_SUPPLIED"]
    round_trip_cost_per_share: Decimal = Field(ge=0, le=10000)
    slippage_bps: Decimal = Field(ge=0, le=100)
    participation_pct: Decimal = Field(gt=0, le=10)
    entry_start: str = "09:45"
    entry_end: str = "11:30"
    force_exit: str = "15:15"
    plans: list[ReplayPlan] = Field(min_length=1, max_length=25)

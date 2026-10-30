"""Pure, offline intraday long-position sizing. Never submits orders."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR

def D(value):
    out=Decimal(str(value))
    if not out.is_finite(): raise ValueError("Non-finite number")
    return out

@dataclass(frozen=True)
class RiskPolicy:
    capital: Decimal = Decimal("980000")
    max_risk_fraction: Decimal = Decimal("0.01")
    max_trades_per_day: int = 1

@dataclass(frozen=True)
class SizingResult:
    quantity: int
    entry: Decimal
    stop: Decimal
    planned_price_risk: Decimal
    estimated_costs: Decimal
    total_planned_risk: Decimal
    gross_exposure: Decimal
    status: str

def size_long(entry, stop, estimated_round_trip_cost_per_share,
              completed_trades_today=0, policy=None):
    p=policy or RiskPolicy()
    entry=D(entry);stop=D(stop);fee=D(estimated_round_trip_cost_per_share)
    capital=D(p.capital);fraction=D(p.max_risk_fraction)
    if entry<=0 or stop<=0 or stop>=entry:
        raise ValueError("Require positive prices with stop strictly below entry")
    if fee<0 or capital<=0 or not (Decimal("0")<fraction<=Decimal("1")):
        raise ValueError("Invalid fee, capital or risk policy")
    if not isinstance(completed_trades_today,int) or completed_trades_today<0:
        raise ValueError("Invalid trade count")
    if completed_trades_today>=p.max_trades_per_day:
        return SizingResult(0,entry,stop,D(0),D(0),D(0),D(0),"BLOCK_DAILY_TRADE_LIMIT")
    per_share_risk=entry-stop+fee
    risk_budget=capital*fraction
    by_risk=int((risk_budget/per_share_risk).to_integral_value(rounding=ROUND_FLOOR))
    by_cash=int((capital/entry).to_integral_value(rounding=ROUND_FLOOR))
    qty=min(by_risk,by_cash)
    if qty<=0:
        return SizingResult(0,entry,stop,D(0),D(0),D(0),D(0),"BLOCK_INSUFFICIENT_CAPITAL_OR_RISK")
    price_risk=(entry-stop)*qty
    estimated_costs=fee*qty
    total=price_risk+estimated_costs
    if total>risk_budget or entry*qty>capital:
        raise AssertionError("Sizing exceeded risk or capital budget")
    return SizingResult(qty,entry,stop,price_risk,estimated_costs,
                        total,entry*qty,"SIZED_REQUIRES_PRETRADE_REVALIDATION")

"""Derive completed paper trades from immutable fills; never invent an exit."""
from datetime import datetime,time
from decimal import Decimal
from src.forward_paper_ledger import instant,amount


def trade_journal(account):
    completed=[];current=None
    if not account:return {"trades":[],"open_trade":None}
    for fill in account["fills"]:
        order=account["orders"][fill["order_id"]]
        q=fill["quantity"];price=Decimal(fill["price"]);fee=Decimal(fill["fee"])
        if fill["side"]=="BUY":
            if current:raise ValueError("Overlapping long fills in paper journal")
            risk=q*(Decimal(order["limit"])-Decimal(order["stop"]))+Decimal(order["fee_budget"])*q/order["quantity"]
            current=dict(symbol=order.get("symbol"),security_id=order.get("security_id"),
                choice_id=order.get("selection",{}).get("human_choice_id"),
                execution_assumptions=order.get("selection",{}).get("execution_assumptions"),
                setup_receipt_id=order.get("selection",{}).get("setup_receipt_id"),
                entry_order_id=fill["order_id"],entry_at=fill["at"],entry_price=price,
                initial_stop=Decimal(order["stop"]),quantity=q,remaining=q,
                fees=fee,exit_value=Decimal(0),planned_risk=risk)
        else:
            if not current or q>current["remaining"]:
                raise ValueError("Exit without matching paper exposure")
            current["remaining"]-=q;current["fees"]+=fee;current["exit_value"]+=price*q
            if not current["remaining"]:
                net=current["exit_value"]-current["entry_price"]*current["quantity"]-current["fees"]
                deadline=datetime.combine(instant(current["entry_at"]).date(),time(15),tzinfo=instant(current["entry_at"]).tzinfo)
                completed.append(dict(symbol=current["symbol"],security_id=current["security_id"],
                    choice_id=current["choice_id"],setup_receipt_id=current["setup_receipt_id"],
                    execution_assumptions=current["execution_assumptions"],
                    entry_order_id=current["entry_order_id"],entry_at=current["entry_at"],exit_at=fill["at"],
                    quantity=current["quantity"],entry=amount(current["entry_price"]),
                    initial_stop=amount(current["initial_stop"]),
                    exit_average=amount(current["exit_value"]/current["quantity"]),
                    fees=amount(current["fees"]),net_pnl=amount(net),planned_risk=amount(current["planned_risk"]),
                    net_r=amount(net/current["planned_risk"]),exit_reason=order["reason"],
                    planned_risk_breached=-net>current["planned_risk"],risk_budget_breached=-net>Decimal("9800"),
                    closure_deadline_breached=instant(fill["at"])>deadline))
                current=None
    open_trade=None if current is None else {k:amount(v) if isinstance(v,Decimal) else v for k,v in current.items()}
    return {"trades":completed[-20:],"open_trade":open_trade}

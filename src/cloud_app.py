"""Cloud MVP skeleton. No order routes, no broker credentials, no real executions."""
import hmac
import os
from pathlib import Path
from fastapi.responses import FileResponse
from decimal import Decimal
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from src.risk_engine import size_long
from src.candle_pipeline import scan_demo

app=FastAPI(title="Intraday Trade Cockpit — Preview Only",version="0.1.0",
            docs_url=None,redoc_url=None)

def require_token(x_access_token: str|None=Header(default=None)):
    expected=os.environ.get("COCKPIT_ACCESS_TOKEN")
    if not expected or not x_access_token or not hmac.compare_digest(x_access_token,expected):
        raise HTTPException(status_code=401,detail="Access denied")
    return True

class PreviewRequest(BaseModel):
    symbol: str = Field(min_length=2,max_length=30,pattern=r"^[A-Z0-9&._-]+$")
    entry: Decimal = Field(gt=0)
    initial_stop: Decimal = Field(gt=0)
    estimated_round_trip_cost_per_share: Decimal = Field(ge=0)
    completed_trades_today: int = Field(default=0,ge=0)

@app.get("/",include_in_schema=False)
def cockpit_page():
    return FileResponse(Path(__file__).parent / "static" / "cockpit.html",
                        media_type="text/html",headers={"Cache-Control":"no-store"})

@app.get("/health")
def health():
    return {"status":"ok","execution_enabled":False,"mode":"PREVIEW_ONLY"}

@app.get("/api/status",dependencies=[Depends(require_token)])
def status():
    return {"mode":"PREVIEW_ONLY","broker_connected":False,
            "execution_enabled":False,"persistent_state_ready":False}

@app.get("/api/demo-setups",dependencies=[Depends(require_token)])
def demo_setups():
    return {"source":"SYNTHETIC_DEMO","live":False,"execution_enabled":False,"setups":scan_demo()}

@app.post("/api/preview",dependencies=[Depends(require_token)])
def preview(request:PreviewRequest):
    try:
        result=size_long(request.entry,request.initial_stop,
                         request.estimated_round_trip_cost_per_share,
                         request.completed_trades_today)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc
    return {"symbol":request.symbol,"status":result.status,"quantity":result.quantity,
            "estimated_total_risk":str(result.total_planned_risk),
            "estimated_costs":str(result.estimated_costs),
            "gross_exposure":str(result.gross_exposure),
            "risk_budget":"9800","execution_enabled":False}

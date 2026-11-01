"""Cloud MVP skeleton. No order routes, no broker credentials, no real executions."""
import hmac
import os
from pathlib import Path
from fastapi.responses import FileResponse, Response
from decimal import Decimal
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from src.risk_engine import size_long
from src.candle_pipeline import scan_demo
from src.candle_input import BatchInput,scan_batch
from src.scan_store import ScanStore
from src.research_snapshot import load_research_snapshot
from src.research_csv import export_research_csv
from src.dhan_history_client import fetch_intraday
from src.dhan_historical_diagnostics import historical_diagnostics
from src.dhan_candle_audit import audit_candles
from src.dhan_raw_timestamps import raw_timestamp_report
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx

app=FastAPI(title="Intraday Trade Cockpit — Preview Only",version="0.1.0",
            docs_url=None,redoc_url=None)

@app.on_event("startup")
def read_only_dhan_smoke_check():
    # Best-effort: logs safe diagnostics; never blocks dashboard startup.
    from threading import Thread
    from src.dhan_startup_audit import run_startup_audit
    Thread(target=run_startup_audit,daemon=True,name="read-only-dhan-audit").start()


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

@app.get("/api/universe-research", dependencies=[Depends(require_token)])
def universe_research():
    try:
        return load_research_snapshot()
    except (OSError, ValueError, TypeError):
        raise HTTPException(status_code=503, detail="Research snapshot unavailable") from None


@app.get("/api/universe-research.csv", dependencies=[Depends(require_token)])
def universe_research_csv():
    try:
        payload=load_research_snapshot()
        content=export_research_csv(payload)
        target=payload["snapshot"]["target_date"]
        return Response(content=content,media_type="text/csv",
                        headers={"Content-Disposition":f'attachment; filename="research-universe-{target}.csv"',
                                 "Cache-Control":"no-store"})
    except (OSError, ValueError, TypeError):
        raise HTTPException(status_code=503,detail="Research CSV unavailable") from None

class HistoryProbe(BaseModel):
    security_id: str = Field(pattern=r"^[0-9]{1,12}$")
    from_date: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")
    to_date: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")
    interval: int = Field(default=5)

@app.get("/api/dhan-status",dependencies=[Depends(require_token)])
def dhan_status():
    return {"token_configured":bool(os.environ.get("DHAN_ACCESS_TOKEN")),
            "live_orders_enabled":False,"historical_read_only":True}

@app.post("/api/dhan-history-probe",dependencies=[Depends(require_token)])
def dhan_history_probe(request:HistoryProbe):
    token=os.environ.get("DHAN_ACCESS_TOKEN")
    if not token:
        return {"status":"DHAN_TOKEN_NOT_CONFIGURED","execution_enabled":False}
    if request.interval not in (5,15):
        raise HTTPException(status_code=422,detail="Only 5 and 15-minute intervals allowed")
    try:
        candles=fetch_intraday(token,request.security_id,request.interval,
                               request.from_date,request.to_date)
    except (httpx.HTTPError,ValueError) as exc:
        # Never return broker error bodies, tokens, or raw instrument data.
        return {"status":"FETCH_FAILED","error_type":type(exc).__name__,
                "execution_enabled":False}
    count=len(candles["timestamp"])
    return {"status":"RECEIVED","interval":request.interval,"candle_count":count,
            "first_epoch":candles["timestamp"][0] if count else None,
            "last_epoch":candles["timestamp"][-1] if count else None,
            "execution_enabled":False,"timestamp_convention_verified":False}

@app.post("/api/dhan-chart-reconciliation", dependencies=[Depends(require_token)])
def dhan_chart_reconciliation():
    """Fixed historical check against Mayur's chart; no order or persistence path."""
    from src.dhan_chart_reconciliation import reconcile_reliance_chart
    token = os.environ.get("DHAN_ACCESS_TOKEN")
    if not token:
        return {"status": "DHAN_TOKEN_NOT_CONFIGURED", "execution_enabled": False,
                "forward_paper_ready": False}
    try:
        # Pad the request to recover Dhan's opening-boundary candle.
        payload = fetch_intraday(token, "2885", 5,
                                 "2026-10-29 09:15:00", "2026-10-31 09:15:00")
        return reconcile_reliance_chart(payload)
    except (httpx.HTTPError, ValueError, OverflowError, TypeError) as exc:
        return {"status": "RECONCILIATION_FAILED", "error_type": type(exc).__name__,
                "execution_enabled": False, "forward_paper_ready": False}


class HistoricalAnalysisRequest(HistoryProbe):
    timestamps_are_open: bool
    cas_eligible: bool | None = None

@app.post("/api/dhan-historical-analysis",dependencies=[Depends(require_token)])
def dhan_historical_analysis(request:HistoricalAnalysisRequest):
    token=os.environ.get("DHAN_ACCESS_TOKEN")
    if not token:return {"status":"DHAN_TOKEN_NOT_CONFIGURED","execution_enabled":False}
    if request.interval!=5:raise HTTPException(status_code=422,detail="Analysis requires 5m candles")
    try:
        payload=fetch_intraday(token,request.security_id,5,
                               request.from_date,request.to_date)
        return historical_diagnostics(payload,timestamps_are_open=request.timestamps_are_open,
            as_of=datetime.now(ZoneInfo("Asia/Kolkata")))
    except (httpx.HTTPError,ValueError,OverflowError,TypeError) as exc:
        return {"status":"ANALYSIS_FAILED","error_type":type(exc).__name__,"execution_enabled":False}

@app.post("/api/dhan-candle-audit",dependencies=[Depends(require_token)])
def dhan_candle_audit(request:HistoricalAnalysisRequest):
    token=os.environ.get("DHAN_ACCESS_TOKEN")
    if not token:return {"status":"DHAN_TOKEN_NOT_CONFIGURED","execution_enabled":False}
    if request.interval!=5:raise HTTPException(status_code=422,detail="Audit requires 5m candles")
    try:
        payload=fetch_intraday(token,request.security_id,5,request.from_date,request.to_date)
        return audit_candles(payload,timestamps_are_open=request.timestamps_are_open,
                             cas_eligible=request.cas_eligible,
                             as_of=datetime.now(ZoneInfo("Asia/Kolkata")))
    except ValueError as exc:
        # Only internal parser messages are surfaced. Broker response bodies remain private.
        safe_reasons={
            "Dhan candle timestamp convention unverified",
            "Missing Dhan parallel OHLCV arrays",
            "Empty or mismatched OHLCV arrays",
            "Invalid epoch",
            "Invalid Dhan candle values",
            "Invalid Dhan session timestamp",
            "Dhan timestamps duplicate or out of order",
        }
        reason=str(exc)
        return {"status":"AUDIT_FAILED","error_type":"ValueError",
                "reason":reason if reason in safe_reasons else "HISTORICAL_DATA_VALIDATION_ERROR",
                "execution_enabled":False}
    except (httpx.HTTPError,OverflowError,TypeError) as exc:
        return {"status":"AUDIT_FAILED","error_type":type(exc).__name__,
                "reason":"DHAN_FETCH_OR_RESPONSE_ERROR","execution_enabled":False}

@app.post("/api/dhan-raw-timestamps",dependencies=[Depends(require_token)])
def dhan_raw_timestamps(request:HistoryProbe):
    token=os.environ.get("DHAN_ACCESS_TOKEN")
    if not token:return {"status":"DHAN_TOKEN_NOT_CONFIGURED","execution_enabled":False}
    if request.interval!=5:raise HTTPException(status_code=422,detail="Only 5m supported")
    try:
        data=fetch_intraday(token,request.security_id,5,request.from_date,request.to_date)
        return raw_timestamp_report(data)
    except (httpx.HTTPError,ValueError,OverflowError,TypeError) as exc:
        return {"status":"RAW_REPORT_FAILED","error_type":type(exc).__name__,
                "execution_enabled":False}

@app.get("/api/demo-setups",dependencies=[Depends(require_token)])
def demo_setups():
    return {"source":"SYNTHETIC_DEMO","live":False,"execution_enabled":False,"setups":scan_demo()}

@app.post("/api/scan-candles",dependencies=[Depends(require_token)])
def scan_candles(request:BatchInput):
    return {"source":"USER_SUPPLIED_CANDLES","live":False,
            "execution_enabled":False,"setups":scan_batch(request)}

@app.get("/api/latest-scan",dependencies=[Depends(require_token)])
def latest_scan():
    url=os.environ.get("SCAN_DATABASE_URL")
    if not url:
        return {"status":"STORE_NOT_CONFIGURED","live":False,"execution_enabled":False}
    from src.universe_scanner import UniverseScanStore, cockpit_snapshot
    try:
        full = UniverseScanStore(url).latest_scan()
        if full is not None:
            return cockpit_snapshot(full)
    except Exception:
        raise HTTPException(status_code=503,detail="Stored universe scan temporarily unavailable") from None
    store=ScanStore(url)
    store.initialize()
    snapshot=store.latest()
    return {"status":"AVAILABLE" if snapshot else "NO_SCANS","source":"PERSISTED_SNAPSHOT",
            "live":False,"execution_enabled":False,"snapshot":snapshot}

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

# Paper simulation has its own authenticated router; no live order integration.
from src.paper_routes import create_paper_router
app.include_router(create_paper_router(require_token))
from src.paper_choice_routes import create_choice_router
app.include_router(create_choice_router(require_token))

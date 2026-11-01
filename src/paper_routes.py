"""Authenticated simulation endpoints. No broker client imports or order routes."""
import csv
import io
import json
import os
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import ValidationError
from src.paper_engine import replay
from src.paper_models import ReplayRequest
from src.paper_scenarios import scenario_suite
from src.paper_store import PaperStore

def create_paper_router(require_token):
    router=APIRouter(prefix="/api/paper",dependencies=[Depends(require_token)])
    def database():
        url=os.environ.get("SCAN_DATABASE_URL")
        return PaperStore(url) if url else None

    def saved(run_id):
        if not re.fullmatch(r"[0-9a-f]{64}",run_id):raise HTTPException(404,"Paper run not found")
        try:
            store=database()
            result=store.get(run_id) if store else None
        except Exception:
            raise HTTPException(503,"Paper journal unavailable") from None
        if result is None:raise HTTPException(404,"Paper run not found")
        return result

    @router.get("/scenarios")
    def scenarios(response: Response):
        response.headers["Cache-Control"]="no-store"
        return scenario_suite()

    @router.post("/replay")
    async def run(request: Request, response: Response):
        response.headers["Cache-Control"]="no-store"
        body=bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body)>2_000_000:raise HTTPException(413,"Paper replay exceeds 2 MB")
        try:
            data=ReplayRequest.model_validate_json(bytes(body))
            result=replay(data)
        except (ValueError,ValidationError):
            raise HTTPException(422,"Invalid replay: check finite OHLC/EMA values, unique plans, contiguous completed 5m bars, signal timing and session dates/windows") from None
        try:
            store=database()
            inserted=store.save(data,result) if store else False
        except Exception:
            raise HTTPException(503,"Paper result could not be saved; retrying the same input is safe") from None
        return {"result":result,"input":data.model_dump(mode="json"),"persisted":store is not None,
                "duplicate":store is not None and not inserted,
                "persistence_note":"Saved to append-only paper journal" if store else "Journal database is not configured; download this result before leaving"}

    @router.get("/runs")
    def runs(response: Response):
        response.headers["Cache-Control"]="no-store"
        try:
            store=database()
            return {"runs":store.recent() if store else [],"persistent":store is not None,"execution_enabled":False}
        except Exception:
            raise HTTPException(503,"Paper journal unavailable") from None

    @router.get("/runs/{run_id}")
    def get_run(run_id: str,response: Response):
        response.headers["Cache-Control"]="no-store"
        return saved(run_id)

    @router.get("/runs/{run_id}/trades.csv")
    def trade_csv(run_id: str):
        data=saved(run_id)["result"]
        fields=["plan_id","symbol","quantity","entry","exit_average","entry_bar_close","exit_bar_close","exit_reason","fees","net_pnl","planned_risk","net_r","risk_budget_breached","exit_fill_at","closure_deadline_breached"]
        output=io.StringIO(newline="");writer=csv.DictWriter(output,fieldnames=fields)
        writer.writeheader()
        for row in data["trades"]:
            writer.writerow({k:("'"+v if isinstance(v,str) and v.startswith(("=","+","-","@","\t","\r")) and k in ("plan_id","symbol") else v) for k,v in row.items()})
        return Response(output.getvalue(),media_type="text/csv",headers={"Cache-Control":"no-store","Content-Disposition":f'attachment; filename="paper-trades-{run_id[:12]}.csv"'})
    return router

"""Authenticated human stock-choice API. Selection is never an order."""
from datetime import datetime
import os
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.forward_paper_ledger import IST
from src.paper_choice import PaperChoiceStore, ChoiceConflict


class ChoiceCommand(BaseModel):
    model_config=ConfigDict(extra="forbid")
    action:Literal["CHOOSE","WITHDRAW"]
    request_id:str=Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")
    expected_choice_id:str|None=Field(default=None,pattern=r"^[a-f0-9]{64}$")
    receipt_id:str|None=Field(default=None,pattern=r"^[a-f0-9]{64}$")
    @model_validator(mode="after")
    def valid(self):
        if (self.action=="CHOOSE")!=(self.receipt_id is not None):
            raise ValueError("Choose requires only a stored receipt; withdraw has none")
        return self


def create_choice_router(require_token,*,clock=lambda:datetime.now(IST)):
    router=APIRouter(prefix="/api/paper",dependencies=[Depends(require_token)])
    def backend():
        url=os.getenv("SCAN_DATABASE_URL")
        if not url:raise HTTPException(503,"Paper workspace database is not configured.")
        return PaperChoiceStore(url)
    @router.get("/workspace")
    def workspace(response:Response):
        response.headers["Cache-Control"]="no-store"
        try:return backend().workspace(clock())
        except HTTPException:raise
        except Exception:raise HTTPException(503,"Paper workspace is temporarily unavailable.") from None
    @router.post("/choice")
    def choose(command:ChoiceCommand,response:Response):
        response.headers["Cache-Control"]="no-store"
        try:return backend().choose(command.model_dump(),clock())
        except ChoiceConflict as exc:raise HTTPException(409,str(exc)) from None
        except HTTPException:raise
        except Exception:raise HTTPException(503,"Selection could not be saved. Retry the same request safely.") from None
    return router

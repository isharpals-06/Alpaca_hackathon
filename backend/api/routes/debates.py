from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.models.contracts import Debate
from backend.orchestration.debate import debate_orchestrator
from backend.scanner.options_scanner import options_scanner
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("/{id}", response_model=Debate)
async def get_debate(id: str):
    debate = await db_repository.get_debate(id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate transcript not found")
    return debate

@router.post("/run")
async def run_debate(
    opportunity_id: Optional[str] = Query(None, description="Existing Opportunity ID to debate"),
    symbol: Optional[str] = Query(None, description="Ticker symbol to scan and debate directly"),
):
    """
    Executes a full 3-phase AI Council debate (Option A: supports both opportunity_id or symbol).
    """
    opp = None
    if opportunity_id:
        opp = await db_repository.get_opportunity(opportunity_id)
        if not opp:
            raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")
    elif symbol:
        opp = await options_scanner.scan_symbol(symbol.upper())
        if not opp:
            raise HTTPException(status_code=400, detail=f"Failed to scan symbol {symbol}")
        await db_repository.save_opportunity(opp)
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'opportunity_id' or 'symbol' query parameter.",
        )

    debate, decision = await debate_orchestrator.run_full_debate(opp)
    return {
        "message": f"Debate completed for {opp.symbol}",
        "debate_id": debate.id,
        "decision": decision.model_dump(mode="json"),
        "debate": debate.model_dump(mode="json"),
    }

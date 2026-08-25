from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.models.contracts import Opportunity
from backend.scanner.options_scanner import options_scanner
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Opportunity])
async def list_opportunities(limit: int = Query(default=20, ge=1, le=100)):
    opps = await db_repository.list_opportunities(limit=limit)
    if not opps:
        # If none cached yet, run a fast universe scan
        opps = await options_scanner.scan_universe()
    return opps

@router.get("/{id}", response_model=Opportunity)
async def get_opportunity(id: str):
    opp = await db_repository.get_opportunity(id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp

@router.post("/scan", response_model=List[Opportunity])
async def trigger_scan(symbol: Optional[str] = None):
    if symbol:
        opp = await options_scanner.scan_symbol(symbol)
        if opp:
            await db_repository.save_opportunity(opp)
            return [opp]
        raise HTTPException(status_code=400, detail=f"Failed to scan symbol {symbol}")
    return await options_scanner.scan_universe()

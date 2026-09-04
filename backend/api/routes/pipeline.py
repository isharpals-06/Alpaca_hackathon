from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.scanner.options_scanner import options_scanner
from backend.orchestration.graph import run_full_pipeline_cycle

router = APIRouter()

class PipelineCycleRequest(BaseModel):
    symbol: Optional[str] = "SPY"

@router.post("/scan/run")
async def trigger_scan():
    """Manually triggers a full universe scan."""
    try:
        opportunities = await options_scanner.scan_universe()
        return {
            "message": "Scan completed successfully",
            "count": len(opportunities),
            "opportunities": opportunities,
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@router.post("/run-cycle")
async def trigger_full_cycle(req: Optional[PipelineCycleRequest] = None):
    """
    Manually triggers one complete autonomous trading cycle:
    Scan -> 5-Agent Council -> Debate -> PM Decision -> Risk Gate -> Alpaca Execution -> Persist.
    """
    symbol = req.symbol if req and req.symbol else "SPY"
    try:
        result = await run_full_pipeline_cycle(symbol)
        return {
            "message": "End-to-end pipeline cycle completed",
            "symbol": symbol,
            "decision": result["decision"],
            "debate": result["debate"],
            "risk_assessment": result["risk_assessment"],
            "order": result["order"],
            "position": result["position"],
        }
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.models.contracts import Position
from backend.monitoring.position_monitor import position_monitor
from backend.monitoring.wheel_loop import wheel_manager
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Position])
async def list_positions():
    return await db_repository.list_positions()

@router.get("/{id}", response_model=Position)
async def get_position(id: str):
    positions = await db_repository.list_positions()
    for p in positions:
        if p.id == id:
            return p
    raise HTTPException(status_code=404, detail="Position not found")

@router.post("/{id}/tick", response_model=Position)
async def tick_position(
    id: str,
    market_premium: Optional[float] = Query(None, description="Current market price of option"),
    delta: Optional[float] = Query(None, description="Current delta of option"),
):
    """Evaluates a single position against the 3 monitoring rules."""
    positions = await db_repository.list_positions()
    target: Optional[Position] = None
    for p in positions:
        if p.id == id:
            target = p
            break
    if not target:
        raise HTTPException(status_code=404, detail=f"Position {id} not found")

    evaluated = position_monitor.evaluate_position(target, market_premium, delta)
    await db_repository.update_position(
        id,
        {
            "current_premium": evaluated.current_premium,
            "unrealized_pnl": evaluated.unrealized_pnl,
            "recommendation": evaluated.recommendation.value,
            "recommendation_reason": evaluated.recommendation_reason,
        },
    )
    return evaluated

@router.post("/tick-all", response_model=List[Position])
async def tick_all():
    """Triggers a monitoring tick on all open positions."""
    return await position_monitor.tick_all_positions()

@router.post("/{id}/close", response_model=Position)
async def close_position(
    id: str,
    close_price: Optional[float] = Query(None, description="Closing price for option buy-back"),
):
    """Closes an open position and locks in realized P&L."""
    closed = await wheel_manager.handle_position_close(id, close_price)
    if not closed:
        raise HTTPException(status_code=404, detail=f"Position {id} not found")
    return closed

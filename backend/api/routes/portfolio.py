from fastapi import APIRouter
from backend.execution.alpaca_client import alpaca_execution
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("")
async def get_portfolio():
    state = await alpaca_execution.get_account_state()
    data = state.model_dump(mode="json")
    positions = await db_repository.list_positions()
    data["unrealized_pnl"] = sum(p.unrealized_pnl for p in positions)
    data["realized_pnl"] = sum(p.realized_pnl for p in positions)
    return data

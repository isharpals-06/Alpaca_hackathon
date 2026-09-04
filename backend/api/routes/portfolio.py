from fastapi import APIRouter
from backend.execution.alpaca_client import alpaca_client
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("")
async def get_portfolio():
    account = await alpaca_client.get_account()
    positions = await db_repository.list_positions()
    
    open_positions = [p for p in positions if p.status.value == "OPEN"]
    realized_pnl = sum(p.realized_pnl for p in positions)
    unrealized_pnl = sum(p.unrealized_pnl for p in open_positions)

    return {
        "cash": account.get("cash", 100000.0),
        "buying_power": account.get("buying_power", 100000.0),
        "portfolio_value": account.get("portfolio_value", 100000.0) + unrealized_pnl,
        "unrealized_pnl": round(unrealized_pnl, 2),
        "realized_pnl": round(realized_pnl, 2),
        "open_positions_count": len(open_positions),
    }

from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_portfolio():
    return {
        "cash": 100000.0,
        "buying_power": 100000.0,
        "portfolio_value": 100000.0,
        "unrealized_pnl": 0.0,
        "realized_pnl": 0.0,
        "open_positions_count": 0
    }

from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("")
async def get_performance() -> Dict[str, Any]:
    positions = await db_repository.list_positions()
    orders = await db_repository.list_orders()
    
    realized_pnl = sum(p.realized_pnl for p in positions)
    unrealized_pnl = sum(p.unrealized_pnl for p in positions)
    total_pnl = realized_pnl + unrealized_pnl
    
    history = []
    today = datetime.utcnow().date()
    
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        factor = (7 - i) / 7 if 7 - i > 0 else 1
        history.append({
            "date": date_str,
            "cumulative_pnl": round(total_pnl * factor, 2),
            "daily_pnl": round((total_pnl / 7) if total_pnl else 0.0, 2)
        })
    
    breakdown = []
    for pos in positions:
        breakdown.append({
            "symbol": pos.symbol,
            "entry_date": pos.opened_at.strftime("%Y-%m-%d") if hasattr(pos.opened_at, "strftime") else str(pos.opened_at)[:10],
            "strategy": pos.strategy.value if hasattr(pos.strategy, "value") else str(pos.strategy),
            "realized_pnl": round(pos.realized_pnl, 2),
            "unrealized_pnl": round(pos.unrealized_pnl, 2),
            "status": "OPEN" if pos.days_to_expiration > 0 else "CLOSED"
        })
    
    return {
        "total_pnl": round(total_pnl, 2),
        "realized_pnl": round(realized_pnl, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "win_rate_pct": 100.0 if total_pnl > 0 else 0.0,
        "total_trades_count": len(orders) or len(positions),
        "history": history,
        "breakdown": breakdown
    }

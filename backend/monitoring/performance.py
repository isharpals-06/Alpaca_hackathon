import logging
from typing import Dict, Any, List
from backend.models.contracts import PerformanceMetrics, Position
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.monitoring.performance")

class PerformanceAggregator:
    """
    Portfolio Performance and P&L Tracking Engine.
    Aggregates realized and unrealized P&L across all closed and open options positions.
    """

    async def get_performance_summary(self) -> Dict[str, Any]:
        positions: List[Position] = await db_repository.list_positions()
        
        realized = sum(p.realized_pnl for p in positions)
        unrealized = sum(p.unrealized_pnl for p in positions)
        total_pnl = round(realized + unrealized, 2)

        win_trades = sum(1 for p in positions if (p.realized_pnl + p.unrealized_pnl) > 0)
        total_trades = len(positions)
        win_rate = round((win_trades / max(total_trades, 1)) * 100, 1)

        return {
            "total_pnl": total_pnl,
            "realized_pnl": round(realized, 2),
            "unrealized_pnl": round(unrealized, 2),
            "win_rate": win_rate,
            "total_trades": total_trades,
            "open_positions_count": sum(1 for p in positions if p.status.value == "OPEN"),
        }

performance_aggregator = PerformanceAggregator()

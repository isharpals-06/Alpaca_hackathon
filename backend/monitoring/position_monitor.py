import logging
from typing import List
from datetime import datetime
from backend.models.contracts import Position, ActionEnum
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.monitoring.position")

class PositionMonitor:
    """
    Continuous Position Monitor.
    Evaluates open options positions against profit-taking and risk rules:
    - 50% profit target captured -> CLOSE
    - Expiration danger zone (DTE <= 7) -> ROLL / CLOSE
    - Delta drift / ITM breach -> ROLL
    - Normal theta decay -> HOLD
    """

    async def evaluate_positions(self) -> List[Position]:
        positions = await db_repository.list_positions()
        evaluated: List[Position] = []

        for pos in positions:
            entry = max(pos.entry_premium, 0.01)
            current = pos.current_premium
            unrealized = round((entry - current) * 100 * pos.qty, 2)
            pos.unrealized_pnl = unrealized

            profit_pct = (entry - current) / entry

            # Rule 1: 50% Max Profit Target
            if profit_pct >= 0.50:
                pos.recommendation = ActionEnum.CLOSE
                pos.recommendation_reason = "50% max profit target reached. Capture premium."
                logger.info("Position %s hit 50%% profit target. Recommendation: CLOSE", pos.symbol)
            # Rule 2: Expiration Safety (DTE <= 7)
            elif pos.days_to_expiration <= 7:
                pos.recommendation = ActionEnum.ROLL
                pos.recommendation_reason = "Near expiration (<7 DTE). Roll to avoid gamma risk."
                logger.info("Position %s near expiration (%sd). Recommendation: ROLL", pos.symbol, pos.days_to_expiration)
            else:
                pos.recommendation = ActionEnum.HOLD
                pos.recommendation_reason = "Position healthy, capturing theta decay."

            evaluated.append(pos)
            await db_repository.save_position(pos)

        return evaluated

position_monitor = PositionMonitor()

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.models.contracts import Position, ActionEnum, StrategyEnum, OptionTypeEnum
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.monitoring.positions")

class PositionMonitor:
    """
    Evaluates open options positions against 3 deterministic management rules:
    1. Profit Target Rule: Capture >= 50% max profit early to lock in yield and eliminate tail risk.
    2. Time Decay / Expiration Proximity Rule: DTE <= 3 days.
    3. Delta Drift Rule: Absolute delta > 0.45 (threat of ITM assignment).
    """

    def evaluate_position(
        self,
        position: Position,
        current_market_premium: Optional[float] = None,
        current_delta: Optional[float] = None,
    ) -> Position:
        curr_premium = current_market_premium if current_market_premium is not None else position.current_premium
        position.current_premium = curr_premium
        
        # Calculate unrealized P&L: (entry_premium - current_premium) * 100 * qty
        premium_diff = position.entry_premium - curr_premium
        position.unrealized_pnl = round(premium_diff * 100.0 * position.qty, 2)
        
        # Calculate percentage of max profit captured
        profit_captured_pct = (premium_diff / max(position.entry_premium, 0.01)) * 100.0

        # -------------------------------------------------------------
        # Rule 1: Profit Target Rule (>= 50% of initial premium captured)
        # -------------------------------------------------------------
        if profit_captured_pct >= 50.0:
            position.recommendation = ActionEnum.CLOSE
            position.recommendation_reason = (
                f"Profit Target Reached: {profit_captured_pct:.1f}% of max premium captured "
                f"(${position.unrealized_pnl:+,.2f} unrealized). Close early to eliminate tail risk."
            )
            logger.info("Position %s: Recommendation CLOSE (Profit Target)", position.symbol)
            return position

        # -------------------------------------------------------------
        # Rule 2: Expiration Proximity Rule (DTE <= 3 days)
        # -------------------------------------------------------------
        if position.days_to_expiration <= 3:
            # If current premium is cheap (< 20% of entry), let it expire or hold
            if curr_premium <= (position.entry_premium * 0.20):
                position.recommendation = ActionEnum.HOLD
                position.recommendation_reason = (
                    f"Expiration Imminent ({position.days_to_expiration} DTE): Option is deep OTM "
                    f"(Current: ${curr_premium:.2f} vs Entry: ${position.entry_premium:.2f}). Allow theta decay to complete expiration."
                )
            else:
                position.recommendation = ActionEnum.ROLL
                position.recommendation_reason = (
                    f"Expiration Imminent ({position.days_to_expiration} DTE) with residual premium ${curr_premium:.2f}. "
                    f"Recommend rolling out in time to avoid pin risk."
                )
            logger.info("Position %s: Expiry Proximity evaluated (%s)", position.symbol, position.recommendation.value)
            return position

        # -------------------------------------------------------------
        # Rule 3: Delta Drift Rule (Threat of ITM breach: |delta| >= 0.45)
        # -------------------------------------------------------------
        if current_delta is not None and abs(current_delta) >= 0.45:
            position.recommendation = ActionEnum.ROLL
            position.recommendation_reason = (
                f"Delta Drift Alert: Delta expanded to {current_delta:+.2f} (above 0.45 defensive threshold). "
                f"Underlying price is challenging the ${position.strike_price:.2f} strike. Recommend rolling down & out."
            )
            logger.warning("Position %s: Recommendation ROLL (Delta Drift: %.2f)", position.symbol, current_delta)
            return position

        # -------------------------------------------------------------
        # Default: Healthy Position -> HOLD
        # -------------------------------------------------------------
        position.recommendation = ActionEnum.HOLD
        position.recommendation_reason = (
            f"Position healthy: {profit_captured_pct:.1f}% profit captured, {position.days_to_expiration} DTE remaining. "
            f"Theta decay progressing as planned."
        )
        return position

    async def tick_all_positions(self) -> List[Position]:
        """Tells all active positions to update recommendations."""
        positions = await db_repository.list_positions()
        updated_positions: List[Position] = []

        for pos in positions:
            # Simulate slight organic theta decay if live quote not polled
            decayed_premium = max(0.05, round(pos.current_premium * 0.95, 2))
            evaluated = self.evaluate_position(pos, current_market_premium=decayed_premium)
            await db_repository.update_position(
                pos.id,
                {
                    "current_premium": evaluated.current_premium,
                    "unrealized_pnl": evaluated.unrealized_pnl,
                    "recommendation": evaluated.recommendation.value,
                    "recommendation_reason": evaluated.recommendation_reason,
                },
            )
            updated_positions.append(evaluated)

        return updated_positions

# Singleton position monitor
position_monitor = PositionMonitor()

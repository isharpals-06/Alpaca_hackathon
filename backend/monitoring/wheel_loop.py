import logging
from typing import Optional, Dict, Any
from datetime import datetime

from backend.models.contracts import Position, ActionEnum, StrategyEnum, OptionTypeEnum
from backend.db.supabase_client import db_repository

logger = logging.getLogger("backend.monitoring.wheel")

class WheelLifecycleManager:
    """
    Manages transitions of the Options Income Wheel strategy:
    1. Position Close: Locks in realized P&L and frees capital.
    2. Expiration Worthless: Captures 100% max premium, routes capital back to CSP scanning.
    3. Assignment: CSP assignment acquires 100 shares, routing underlying to Covered Call scanning.
    """

    async def handle_position_close(
        self,
        position_id: str,
        close_price: Optional[float] = None,
    ) -> Optional[Position]:
        positions = await db_repository.list_positions()
        target: Optional[Position] = None
        for p in positions:
            if p.id == position_id:
                target = p
                break

        if not target:
            logger.warning("Position %s not found for close", position_id)
            return None

        exit_premium = close_price if close_price is not None else target.current_premium
        realized = round((target.entry_premium - exit_premium) * 100.0 * target.qty, 2)

        updated = await db_repository.update_position(
            position_id,
            {
                "current_premium": exit_premium,
                "unrealized_pnl": 0.0,
                "realized_pnl": realized,
                "recommendation": ActionEnum.CLOSE.value,
                "recommendation_reason": f"Position closed at ${exit_premium:.2f}. Realized P&L: ${realized:+,.2f}.",
            },
        )
        logger.info("Closed position %s -> Realized P&L: $%.2f", target.symbol, realized)
        return updated

    async def handle_position_expiry(self, position_id: str) -> Optional[Position]:
        """Option expired completely worthless: 100% premium retained."""
        return await self.handle_position_close(position_id, close_price=0.0)

    async def handle_position_assignment(self, position_id: str) -> Optional[Dict[str, Any]]:
        """CSP Assigned: 100 shares assigned at strike price, ready for Covered Calls."""
        closed_pos = await self.handle_position_close(position_id, close_price=0.0)
        if not closed_pos:
            return None

        return {
            "status": "ASSIGNED",
            "symbol": closed_pos.underlying_symbol,
            "shares_acquired": 100 * closed_pos.qty,
            "cost_basis": closed_pos.strike_price - closed_pos.entry_premium,
            "next_wheel_strategy": StrategyEnum.COVERED_CALL.value,
            "message": f"Assigned {closed_pos.underlying_symbol} @ ${closed_pos.strike_price:.2f}. Effective cost basis: ${closed_pos.strike_price - closed_pos.entry_premium:.2f}. Ready for Covered Call writing.",
        }

# Singleton wheel manager
wheel_manager = WheelLifecycleManager()

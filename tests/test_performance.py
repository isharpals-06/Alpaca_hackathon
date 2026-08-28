import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from datetime import datetime
from backend.models.contracts import Position, StrategyEnum, OptionTypeEnum, ActionEnum
from backend.db.supabase_client import db_repository
from backend.monitoring.performance import performance_aggregator
from backend.monitoring.wheel_loop import wheel_manager

class TestPerformanceAndWheel(unittest.TestCase):
    def test_performance_calculation_and_wheel_close(self):
        async def run_test():
            # 1. Save a sample position
            pos = Position(
                symbol="AAPL260918P00215000",
                underlying_symbol="AAPL",
                strategy=StrategyEnum.CASH_SECURED_PUT,
                option_type=OptionTypeEnum.PUT,
                strike_price=215.0,
                expiration_date="2026-09-18",
                qty=1,
                entry_premium=3.50,
                current_premium=1.50,
                unrealized_pnl=200.0,
                realized_pnl=0.0,
                days_to_expiration=20,
                recommendation=ActionEnum.CLOSE,
                opened_at=datetime.utcnow(),
                last_checked_at=datetime.utcnow(),
            )
            await db_repository.save_position(pos)

            # 2. Compute performance metrics
            perf = await performance_aggregator.calculate_performance()
            self.assertGreaterEqual(perf.total_unrealized_pnl, 200.0)
            self.assertGreaterEqual(perf.win_rate_pct, 50.0)

            # 3. Test Wheel close
            closed_pos = await wheel_manager.handle_position_close(pos.id, close_price=1.20)
            self.assertIsNotNone(closed_pos)
            self.assertEqual(closed_pos.realized_pnl, 230.0)  # ($3.50 - $1.20) * 100

            # 4. Verify equity history
            history = await performance_aggregator.get_performance_history(days=7)
            self.assertEqual(len(history), 8)
            self.assertIn("portfolio_value", history[-1])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

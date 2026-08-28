import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
from datetime import datetime
from backend.models.contracts import Position, ActionEnum, StrategyEnum, OptionTypeEnum
from backend.monitoring.position_monitor import position_monitor

class TestPositionMonitor(unittest.TestCase):
    def setUp(self):
        self.base_position = Position(
            symbol="SPY260918P00540000",
            underlying_symbol="SPY",
            strategy=StrategyEnum.CASH_SECURED_PUT,
            option_type=OptionTypeEnum.PUT,
            strike_price=540.0,
            expiration_date="2026-09-18",
            qty=1,
            entry_premium=4.00,
            current_premium=4.00,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            days_to_expiration=30,
            recommendation=ActionEnum.HOLD,
            opened_at=datetime.utcnow(),
            last_checked_at=datetime.utcnow(),
        )

    def test_profit_target_rule_fires_close(self):
        # Premium dropped from $4.00 to $1.60 (60% profit captured)
        evaluated = position_monitor.evaluate_position(self.base_position, current_market_premium=1.60)
        self.assertEqual(evaluated.recommendation, ActionEnum.CLOSE)
        self.assertEqual(evaluated.unrealized_pnl, 240.0)  # ($4.00 - $1.60) * 100
        self.assertIn("Profit Target Reached", evaluated.recommendation_reason)

    def test_delta_drift_rule_fires_roll(self):
        # Stock dropped, put delta expanded to -0.48 (near ITM)
        evaluated = position_monitor.evaluate_position(
            self.base_position,
            current_market_premium=5.20,
            current_delta=-0.48,
        )
        self.assertEqual(evaluated.recommendation, ActionEnum.ROLL)
        self.assertIn("Delta Drift Alert", evaluated.recommendation_reason)

    def test_expiry_proximity_rule(self):
        # 2 DTE remaining, profit captured is only 40% ($4.00 down to $2.40), but near expiration with low delta
        pos_near_exp = self.base_position.model_copy()
        pos_near_exp.days_to_expiration = 2
        pos_near_exp.entry_premium = 4.00
        pos_near_exp.current_premium = 2.40
        # Premium > 20% of entry ($2.40 > $0.80) -> recommends ROLL to manage expiration
        evaluated = position_monitor.evaluate_position(pos_near_exp, current_market_premium=2.40)
        self.assertEqual(evaluated.recommendation, ActionEnum.ROLL)
        self.assertIn("Expiration Imminent", evaluated.recommendation_reason)

    def test_healthy_position_holds(self):
        # Normal decay: $4.00 down to $3.20 (20% profit), 25 DTE, normal delta -0.22
        evaluated = position_monitor.evaluate_position(
            self.base_position,
            current_market_premium=3.20,
            current_delta=-0.22,
        )
        self.assertEqual(evaluated.recommendation, ActionEnum.HOLD)
        self.assertIn("Position healthy", evaluated.recommendation_reason)

if __name__ == "__main__":
    unittest.main()

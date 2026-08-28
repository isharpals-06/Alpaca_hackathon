import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
from datetime import datetime
from backend.models.contracts import (
    ContractSpec,
    PortfolioState,
    StrategyEnum,
    OptionTypeEnum,
)
from backend.risk.engine import risk_engine
from backend.risk.checks import (
    check_contract_validity,
    check_position_sizing,
    check_total_options_exposure,
    check_sector_concentration,
    check_assignment_collateral,
)

class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.contract = ContractSpec(
            symbol="SPY260918P00540000",
            underlying_symbol="SPY",
            strategy_type=StrategyEnum.CASH_SECURED_PUT,
            option_type=OptionTypeEnum.PUT,
            strike_price=540.0,
            expiration_date="2026-09-18",
            days_to_expiration=30,
            delta=-0.22,
            premium_estimate=3.85,
            contracts_count=1,
            max_loss_estimate=54000.0,
            liquidity_score=0.92,
        )
        self.portfolio = PortfolioState(
            cash=100000.0,
            buying_power=400000.0,
            portfolio_value=100000.0,
            options_collateral_used=0.0,
            open_positions_count=0,
            positions=[],
            as_of=datetime.utcnow(),
        )

    def test_compliant_trade_approval(self):
        assessment = risk_engine.evaluate_trade(self.contract, self.portfolio)
        self.assertTrue(assessment.approved)
        self.assertEqual(len(assessment.checks_failed), 0)
        self.assertEqual(len(assessment.checks_passed), 5)

    def test_insufficient_cash_collateral_veto(self):
        # Reduce cash below required $54,000
        poor_portfolio = PortfolioState(
            cash=20000.0,
            buying_power=80000.0,
            portfolio_value=20000.0,
            options_collateral_used=0.0,
            open_positions_count=0,
            positions=[],
            as_of=datetime.utcnow(),
        )
        assessment = risk_engine.evaluate_trade(self.contract, poor_portfolio)
        self.assertFalse(assessment.approved)
        self.assertIn("Assignment Collateral", assessment.checks_failed)
        self.assertIsNotNone(assessment.veto_reason)

    def test_simulated_demo_veto(self):
        assessment = risk_engine.evaluate_trade(self.contract, self.portfolio, simulate_veto=True)
        self.assertFalse(assessment.approved)
        self.assertIn("Position Sizing (Simulated)", assessment.checks_failed)

if __name__ == "__main__":
    unittest.main()

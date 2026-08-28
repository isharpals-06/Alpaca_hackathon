import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
from backend.models.contracts import (
    Opportunity,
    CandidateContract,
    Decision,
    ActionEnum,
    StrategyEnum,
    OptionTypeEnum,
)
from backend.strategy.cash_secured_put import select_best_csp_contract
from backend.strategy.covered_call import select_best_covered_call_contract
from backend.strategy.engine import strategy_engine

class TestStrategyEngine(unittest.TestCase):
    def setUp(self):
        self.opportunity = Opportunity(
            symbol="SPY",
            underlying_price=560.0,
            historical_volatility=0.18,
            implied_volatility=0.22,
            iv_percentile=65.0,
            liquidity_score=0.92,
            candidate_contracts=[
                CandidateContract(
                    symbol="SPY260918P00540000",
                    underlying_symbol="SPY",
                    option_type=OptionTypeEnum.PUT,
                    strike_price=540.0,
                    expiration_date="2026-09-18",
                    days_to_expiration=30,
                    bid=3.80,
                    ask=3.90,
                    mid_price=3.85,
                    open_interest=2500,
                    volume=800,
                    implied_volatility=0.22,
                    delta=-0.22,
                    liquidity_score=0.94,
                ),
                CandidateContract(
                    symbol="SPY260918C00575000",
                    underlying_symbol="SPY",
                    option_type=OptionTypeEnum.CALL,
                    strike_price=575.0,
                    expiration_date="2026-09-18",
                    days_to_expiration=30,
                    bid=2.50,
                    ask=2.60,
                    mid_price=2.55,
                    open_interest=1800,
                    volume=600,
                    implied_volatility=0.20,
                    delta=0.25,
                    liquidity_score=0.90,
                ),
            ]
        )

    def test_csp_selection(self):
        spec = select_best_csp_contract(self.opportunity)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.strategy_type, StrategyEnum.CASH_SECURED_PUT)
        self.assertEqual(spec.option_type, OptionTypeEnum.PUT)
        self.assertEqual(spec.strike_price, 540.0)
        self.assertEqual(spec.premium_estimate, 3.85)

    def test_covered_call_selection(self):
        spec = select_best_covered_call_contract(self.opportunity)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.strategy_type, StrategyEnum.COVERED_CALL)
        self.assertEqual(spec.option_type, OptionTypeEnum.CALL)
        self.assertEqual(spec.strike_price, 575.0)

    def test_strategy_engine_routing(self):
        decision = Decision(
            opportunity_id=self.opportunity.id,
            symbol="SPY",
            action=ActionEnum.TRADE,
            rationale="Approved",
            confidence_score=0.85,
            recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
        )
        spec = strategy_engine.build_contract_spec(self.opportunity, decision)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.strategy_type, StrategyEnum.CASH_SECURED_PUT)

if __name__ == "__main__":
    unittest.main()

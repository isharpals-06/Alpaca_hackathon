import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from backend.models.contracts import (
    ActionEnum,
    StrategyEnum,
    OptionTypeEnum,
    Opportunity,
    CandidateContract,
    AgentOutput,
    StanceEnum,
    Decision,
)
from backend.db.supabase_client import SupabaseRepository

class TestContractsAndDB(unittest.TestCase):
    def test_models_instantiation_and_validation(self):
        contract = CandidateContract(
            symbol="SPY260918P00540000",
            underlying_symbol="SPY",
            option_type=OptionTypeEnum.PUT,
            strike_price=540.0,
            expiration_date="2026-09-18",
            days_to_expiration=30,
            bid=4.20,
            ask=4.30,
            mid_price=4.25,
            open_interest=1500,
            volume=600,
            implied_volatility=0.22,
            delta=-0.25,
            liquidity_score=0.92,
        )
        self.assertEqual(contract.strike_price, 540.0)
        self.assertEqual(contract.delta, -0.25)

        opp = Opportunity(
            symbol="SPY",
            underlying_price=560.0,
            implied_volatility=0.22,
            iv_percentile=60.0,
            liquidity_score=0.92,
            candidate_contracts=[contract],
        )
        self.assertEqual(opp.symbol, "SPY")
        self.assertEqual(len(opp.candidate_contracts), 1)

        agent_out = AgentOutput(
            agent_name="Quant",
            stance=StanceEnum.BULLISH,
            confidence=0.85,
            thesis="Momentum remains positive above 50-day moving average.",
            claims=["RSI at 54 is neutral-bullish", "Support at $550"],
            risks=["Macro CPI print next week"],
            recommendation="SELL_PUT",
        )
        self.assertEqual(agent_out.confidence, 0.85)

        decision = Decision(
            opportunity_id=opp.id,
            symbol="SPY",
            action=ActionEnum.TRADE,
            rationale="Strong risk-reward on 30-day 0.25 delta put.",
            confidence_score=0.88,
            recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
        )
        self.assertEqual(decision.action, ActionEnum.TRADE)
        self.assertEqual(decision.recommended_strategy, StrategyEnum.CASH_SECURED_PUT)

    def test_supabase_in_memory_repository(self):
        async def run_test():
            repo = SupabaseRepository()
            opp = Opportunity(
                symbol="AAPL",
                underlying_price=225.0,
                implied_volatility=0.25,
                iv_percentile=55.0,
                liquidity_score=0.88,
            )
            saved_opp = await repo.save_opportunity(opp)
            self.assertEqual(saved_opp.id, opp.id)
            
            fetched_opp = await repo.get_opportunity(opp.id)
            self.assertIsNotNone(fetched_opp)
            self.assertEqual(fetched_opp.symbol, "AAPL")

            decision = Decision(
                opportunity_id=opp.id,
                symbol="AAPL",
                action=ActionEnum.TRADE,
                rationale="Favorable IV percentile for put selling",
                confidence_score=0.80,
                recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
            )
            await repo.save_decision(decision)
            decisions = await repo.list_decisions()
            self.assertGreaterEqual(len(decisions), 1)
            self.assertTrue(any(d.id == decision.id for d in decisions))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from backend.models.contracts import Opportunity, CandidateContract, OptionTypeEnum, ActionEnum
from backend.agents.council.quant import run_quant_analysis
from backend.agents.council.volatility import run_volatility_analysis
from backend.agents.council.bull import run_bull_analysis
from backend.agents.council.bear import run_bear_analysis
from backend.agents.council.risk_officer import run_risk_review
from backend.agents.council.portfolio_manager import run_portfolio_manager_synthesis

class TestCouncilAgents(unittest.TestCase):
    def setUp(self):
        self.opportunity = Opportunity(
            symbol="SPY",
            underlying_price=560.0,
            historical_volatility=0.18,
            implied_volatility=0.22,
            iv_percentile=65.0,
            liquidity_score=0.92,
            sector="Index ETF",
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
                    delta=-0.24,
                    liquidity_score=0.94,
                )
            ]
        )

    def test_quant_and_volatility_agents(self):
        async def run_test():
            quant_out = await run_quant_analysis(self.opportunity)
            self.assertEqual(quant_out.agent_name, "Quant")
            self.assertTrue(0.0 <= quant_out.confidence <= 1.0)
            self.assertTrue(len(quant_out.thesis) > 0)

            vol_out = await run_volatility_analysis(self.opportunity)
            self.assertEqual(vol_out.agent_name, "Volatility")
            self.assertTrue(0.0 <= vol_out.confidence <= 1.0)

            bull_out = await run_bull_analysis(self.opportunity, quant_out, vol_out)
            self.assertEqual(bull_out.agent_name, "Bull")
            self.assertTrue(len(bull_out.claims) > 0)

            bear_out = await run_bear_analysis(self.opportunity, quant_out, vol_out)
            self.assertEqual(bear_out.agent_name, "Bear")
            self.assertTrue(len(bear_out.risks) > 0)

            risk_out = await run_risk_review(self.opportunity)
            self.assertEqual(risk_out.agent_name, "Risk Officer")

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

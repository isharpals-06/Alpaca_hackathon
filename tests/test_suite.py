import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from datetime import datetime
from backend.models.contracts import (
    ActionEnum,
    StrategyEnum,
    OptionTypeEnum,
    Opportunity,
    CandidateContract,
    AgentOutput,
    StanceEnum,
    Debate,
    Decision,
)
from backend.db.supabase_client import SupabaseRepository
from backend.scanner.universe import get_curated_symbols, get_symbol_metadata
from backend.scanner.options_scanner import OptionsScanner

class TestContractsAndDB(unittest.TestCase):
    def test_models_instantiation(self):
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

    def test_in_memory_repository(self):
        async def run_test():
            repo = SupabaseRepository()
            opp = Opportunity(
                symbol="AAPL",
                underlying_price=225.0,
                implied_volatility=0.25,
                iv_percentile=55.0,
                liquidity_score=0.88,
            )
            saved = await repo.save_opportunity(opp)
            self.assertEqual(saved.id, opp.id)
            
            fetched = await repo.get_opportunity(opp.id)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.symbol, "AAPL")

            decision = Decision(
                opportunity_id=opp.id,
                symbol="AAPL",
                action=ActionEnum.TRADE,
                rationale="Test rationale",
                confidence_score=0.85,
                recommended_strategy=StrategyEnum.CASH_SECURED_PUT,
            )
            await repo.save_decision(decision)
            decisions = await repo.list_decisions()
            self.assertTrue(any(d.id == decision.id for d in decisions))

        asyncio.run(run_test())

class TestScanner(unittest.TestCase):
    def test_universe(self):
        symbols = get_curated_symbols()
        self.assertIn("SPY", symbols)
        self.assertIn("AAPL", symbols)
        meta = get_symbol_metadata("SPY")
        self.assertEqual(meta["sector"], "Index ETF")

    def test_osi_symbol_parsing(self):
        scanner = OptionsScanner()
        parsed = scanner._parse_osi_symbol("SPY260918P00540000")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["option_type"], "put")
        self.assertEqual(parsed["strike_price"], 540.0)

    def test_scanner_generation(self):
        async def run_test():
            scanner = OptionsScanner()
            opp = await scanner.scan_symbol("AAPL")
            self.assertIsNotNone(opp)
            self.assertEqual(opp.symbol, "AAPL")
            self.assertTrue(len(opp.candidate_contracts) > 0)
            self.assertTrue(any(c.option_type == OptionTypeEnum.PUT for c in opp.candidate_contracts))
            self.assertTrue(any(c.option_type == OptionTypeEnum.CALL for c in opp.candidate_contracts))

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

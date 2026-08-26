import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
import asyncio
from backend.scanner.options_scanner import options_scanner
from backend.orchestration.debate import debate_orchestrator
from backend.orchestration.graph import council_graph
from backend.db.supabase_client import db_repository

class TestDebateOrchestrator(unittest.TestCase):
    def test_end_to_end_debate_cycle(self):
        async def run_test():
            # 1. Scan symbol
            opp = await options_scanner.scan_symbol("AAPL")
            self.assertIsNotNone(opp)
            
            # 2. Run debate
            debate, decision = await debate_orchestrator.run_full_debate(opp)
            
            # Verify debate properties
            self.assertEqual(debate.symbol, "AAPL")
            self.assertEqual(len(debate.agent_outputs), 5)  # Quant, Vol, Bull, Bear, Risk Officer
            self.assertTrue(len(debate.challenges) >= 1)
            self.assertTrue(len(debate.responses) >= 1)
            self.assertIn(decision.action.value, ["TRADE", "NO_TRADE"])
            self.assertTrue(len(decision.rationale) > 0)
            
            # Verify persistence
            stored_debate = await db_repository.get_debate(debate.id)
            self.assertIsNotNone(stored_debate)
            self.assertEqual(stored_debate.id, debate.id)

            # 3. Verify state graph
            graph_res = await council_graph.execute_council_cycle(opp)
            self.assertEqual(graph_res["current_state"], "DECISION_RENDERED")
            self.assertIn(graph_res["next_state"], ["STRATEGY_PROPOSED", "SCANNING"])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()

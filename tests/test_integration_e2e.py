import sys
import os
sys.path.insert(0, os.path.abspath("."))

import unittest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestEndToEndIntegration(unittest.TestCase):
    """
    Day 6 End-to-End Integration & Edge-Case Verification Suite.
    """

    def test_e2e_successful_cycle(self):
        """Test Scenario 1: Standard cycle execution on SPY."""
        res = client.post("/pipeline/run-cycle?symbol=SPY")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "COMPLETED")
        self.assertEqual(data["symbol"], "SPY")
        self.assertIn(data["action_taken"], ["TRADE", "NO_TRADE"])
        self.assertIsNotNone(data["debate"])
        self.assertIsNotNone(data["decision"])
        print(f"  -> Scenario 1 (SPY Cycle): PASSED [Action: {data['action_taken']}]")

    def test_e2e_risk_veto_outcome(self):
        """Test Scenario 2: Deliberate Risk Gate Veto execution."""
        res = client.post("/pipeline/run-cycle?symbol=TSLA&simulate_risk_veto=true")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        if data["action_taken"] == "TRADE":
            self.assertIsNotNone(data["risk_assessment"])
            self.assertFalse(data["risk_assessment"]["approved"])
            self.assertIsNotNone(data["risk_assessment"]["veto_reason"])
            # SAFETY GUARANTEE: Zero orders must be submitted when vetoed
            self.assertIsNone(data["order"])
            self.assertIsNone(data["position"])
            print(f"  -> Scenario 2 (Risk Gate Veto): PASSED [Veto Reason: {data['risk_assessment']['veto_reason']}]")
        else:
            print(f"  -> Scenario 2 (Council chose NO_TRADE before risk gate): PASSED")

    def test_e2e_edge_case_unknown_ticker(self):
        """Test Scenario 3: Graceful fallback for unknown/illiquid ticker."""
        res = client.post("/pipeline/run-cycle?symbol=UNKNOWN123")
        # System should handle gracefully and complete cycle using synthetic fallback
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "COMPLETED")
        print("  -> Scenario 3 (Unknown Ticker Resiliency): PASSED")

    def test_e2e_positions_and_monitoring_lifecycle(self):
        """Test Scenario 4: Monitoring tick and position lifecycle."""
        # 1. Fetch positions
        res = client.get("/positions")
        self.assertEqual(res.status_code, 200)
        
        # 2. Trigger tick on all positions
        res_tick = client.post("/positions/tick-all")
        self.assertEqual(res_tick.status_code, 200)

        # 3. Fetch performance
        res_perf = client.get("/performance")
        self.assertEqual(res_perf.status_code, 200)
        perf_data = res_perf.json()
        self.assertIn("total_realized_pnl", perf_data)
        self.assertIn("win_rate_pct", perf_data)
        print("  -> Scenario 4 (Position Lifecycle & Performance): PASSED")

if __name__ == "__main__":
    unittest.main()

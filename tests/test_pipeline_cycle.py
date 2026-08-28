import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_full_pipeline_run_cycle():
    # 1. Test Pipeline Status
    res_status = client.get("/pipeline/status")
    assert res_status.status_code == 200
    print("[OK] GET /pipeline/status active:", res_status.json()["service"])

    # 2. Test Full Cycle execution with SPY
    res_cycle = client.post("/pipeline/run-cycle?symbol=SPY")
    assert res_cycle.status_code == 200, f"Cycle failed: {res_cycle.text}"
    data = res_cycle.json()
    assert data["status"] == "COMPLETED"
    assert "opportunity" in data
    assert "debate" in data
    assert "decision" in data
    print(f"[OK] POST /pipeline/run-cycle completed for {data['symbol']} -> Action: {data['action_taken']}")
    
    if data["action_taken"] == "TRADE":
        assert data["contract_spec"] is not None
        assert data["risk_assessment"] is not None
        print(f"     Risk Assessment: Approved = {data['risk_assessment']['approved']}")
        if data["risk_assessment"]["approved"]:
            assert data["order"] is not None
            assert data["position"] is not None
            print(f"     Paper Order Submitted: ID {data['order']['alpaca_order_id']}, Status: {data['order']['status']}")

    # 3. Test Full Cycle with Simulated Risk Veto
    res_veto = client.post("/pipeline/run-cycle?symbol=AAPL&simulate_risk_veto=true")
    assert res_veto.status_code == 200
    veto_data = res_veto.json()
    if veto_data["action_taken"] == "TRADE":
        assert veto_data["risk_assessment"]["approved"] is False
        assert "veto_reason" in veto_data["risk_assessment"]
        assert veto_data["order"] is None  # Order must NOT execute when vetoed
        print(f"[OK] Simulated Risk Veto successfully blocked execution! Veto Reason: {veto_data['risk_assessment']['veto_reason']}")

if __name__ == "__main__":
    test_full_pipeline_run_cycle()

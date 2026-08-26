import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_debate_api_endpoints():
    # 1. Trigger debate for SPY directly via query parameter (Option A)
    res = client.post("/debates/run?symbol=SPY")
    assert res.status_code == 200, f"Debate run failed: {res.text}"
    data = res.json()
    assert "debate_id" in data
    assert "decision" in data
    assert data["decision"]["action"] in ["TRADE", "NO_TRADE"]
    debate_id = data["debate_id"]
    print(f"[OK] POST /debates/run?symbol=SPY succeeded! Debate ID: {debate_id}, Action: {data['decision']['action']}")

    # 2. Query debate transcript
    res_debate = client.get(f"/debates/{debate_id}")
    assert res_debate.status_code == 200
    debate_data = res_debate.json()
    assert len(debate_data["agent_outputs"]) == 5
    assert len(debate_data["challenges"]) >= 1
    assert len(debate_data["responses"]) >= 1
    print(f"[OK] GET /debates/{debate_id} retrieved full transcript with 5 agents and cross-examination!")

    # 3. List decisions
    res_decisions = client.get("/decisions")
    assert res_decisions.status_code == 200
    decisions = res_decisions.json()
    assert len(decisions) >= 1
    print(f"[OK] GET /decisions returned {len(decisions)} decisions!")

if __name__ == "__main__":
    test_debate_api_endpoints()

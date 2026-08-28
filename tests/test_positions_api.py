import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_positions_and_performance_api():
    # 1. GET /positions
    res_pos = client.get("/positions")
    assert res_pos.status_code == 200
    positions = res_pos.json()
    print(f"[OK] GET /positions returned {len(positions)} positions")

    # 2. GET /performance
    res_perf = client.get("/performance")
    assert res_perf.status_code == 200
    perf = res_perf.json()
    assert "total_realized_pnl" in perf
    assert "win_rate_pct" in perf
    print(f"[OK] GET /performance: Realized P&L: ${perf['total_realized_pnl']}, Unrealized: ${perf['total_unrealized_pnl']}, Win Rate: {perf['win_rate_pct']}%")

    # 3. GET /performance/history
    res_hist = client.get("/performance/history?days=7")
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert len(history) == 8
    print(f"[OK] GET /performance/history returned {len(history)} equity points for frontend chart")

if __name__ == "__main__":
    test_positions_and_performance_api()

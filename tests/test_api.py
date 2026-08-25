import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("Health check endpoint test: PASSED")

def test_opportunities_endpoint():
    res = client.get("/opportunities?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    print(f"Opportunities endpoint test: PASSED (Returned {len(data)} opportunities)")

if __name__ == "__main__":
    test_health()
    test_opportunities_endpoint()

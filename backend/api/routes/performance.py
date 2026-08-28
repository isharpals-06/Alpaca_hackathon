from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.models.contracts import PerformanceMetrics
from backend.monitoring.performance import performance_aggregator

router = APIRouter()

@router.get("", response_model=PerformanceMetrics)
async def get_performance():
    """Returns aggregate portfolio realized/unrealized P&L, win rate, and stats."""
    return await performance_aggregator.calculate_performance()

@router.get("/history")
async def get_performance_history(days: int = Query(default=14, ge=1, le=90)):
    """Returns historical daily equity curve snapshots for frontend charts."""
    return await performance_aggregator.get_performance_history(days=days)

from fastapi import APIRouter
from typing import List
from backend.models.contracts import Order

router = APIRouter()

@router.get("", response_model=List[Order])
async def list_trades():
    return []

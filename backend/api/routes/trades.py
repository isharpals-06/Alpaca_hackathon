from fastapi import APIRouter
from typing import List
from backend.models.contracts import Order
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Order])
async def list_trades():
    return await db_repository.list_orders()

from fastapi import APIRouter, HTTPException
from typing import List
from backend.models.contracts import Decision
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Decision])
async def list_decisions():
    return await db_repository.list_decisions()

@router.get("/{id}", response_model=Decision)
async def get_decision(id: str):
    dec = await db_repository.get_decision(id)
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    return dec

from fastapi import APIRouter, HTTPException, Query
from typing import List
from backend.models.contracts import Decision
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Decision])
async def list_decisions(limit: int = Query(default=50, ge=1, le=100)):
    return await db_repository.list_decisions(limit=limit)

@router.get("/{id}", response_model=Decision)
async def get_decision(id: str):
    decisions = await db_repository.list_decisions(limit=100)
    for d in decisions:
        if d.id == id:
            return d
    raise HTTPException(status_code=404, detail="Decision not found")

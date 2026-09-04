from fastapi import APIRouter, HTTPException
from typing import List, Optional
from backend.models.contracts import Debate
from backend.db.supabase_client import db_repository

router = APIRouter()

@router.get("", response_model=List[Debate])
async def list_debates(limit: int = 10):
    debates = await db_repository.list_debates(limit=limit)
    return debates

@router.get("/{id}", response_model=Debate)
async def get_debate(id: str):
    debate = await db_repository.get_debate(id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return debate

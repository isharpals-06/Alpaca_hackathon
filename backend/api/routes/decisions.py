from fastapi import APIRouter, HTTPException
from typing import List
from backend.models.contracts import Decision

router = APIRouter()

@router.get("", response_model=List[Decision])
async def list_decisions():
    return []

@router.get("/{id}", response_model=Decision)
async def get_decision(id: str):
    raise HTTPException(status_code=404, detail="Decision not found")

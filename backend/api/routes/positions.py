from fastapi import APIRouter, HTTPException
from typing import List
from backend.models.contracts import Position

router = APIRouter()

@router.get("", response_model=List[Position])
async def list_positions():
    return []

@router.get("/{id}", response_model=Position)
async def get_position(id: str):
    raise HTTPException(status_code=404, detail="Position not found")

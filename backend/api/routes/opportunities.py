from fastapi import APIRouter, HTTPException
from typing import List
from backend.models.contracts import Opportunity

router = APIRouter()

@router.get("", response_model=List[Opportunity])
async def list_opportunities():
    return []

@router.get("/{id}", response_model=Opportunity)
async def get_opportunity(id: str):
    raise HTTPException(status_code=404, detail="Opportunity not found")

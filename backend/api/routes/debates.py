from fastapi import APIRouter, HTTPException
from backend.models.contracts import Debate

router = APIRouter()

@router.get("/{id}", response_model=Debate)
async def get_debate(id: str):
    raise HTTPException(status_code=404, detail="Debate not found")

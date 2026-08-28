from fastapi import APIRouter
from backend.execution.alpaca_client import alpaca_execution

router = APIRouter()

@router.get("")
async def get_portfolio():
    state = await alpaca_execution.get_account_state()
    return state.model_dump(mode="json")

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "alpaca-ai-backend",
        "timestamp": "2026-08-28T00:00:00Z"
    }

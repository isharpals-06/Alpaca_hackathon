from fastapi import APIRouter

router = APIRouter()

@router.post("/scan/run")
async def trigger_scan():
    return {"message": "Scan cycle triggered", "status": "processing"}

@router.post("/run-cycle")
async def trigger_full_cycle():
    return {"message": "End-to-end pipeline cycle triggered", "status": "processing"}

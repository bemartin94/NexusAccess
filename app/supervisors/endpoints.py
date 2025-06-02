from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def supervisors():
    return {"ejemplo": "ejemplo"}
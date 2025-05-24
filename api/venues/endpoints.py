from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def venues():
    return {"ejemplo": "ejemplo"}
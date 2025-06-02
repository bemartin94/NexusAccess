from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def access():
    return {"ejemplo": "ejemplo"}
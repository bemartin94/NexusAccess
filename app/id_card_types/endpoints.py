from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def id_card_types():
    return {"ejemplo": "ejemplo"}
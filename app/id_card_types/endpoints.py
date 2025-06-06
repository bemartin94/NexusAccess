from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.id_card_types import schemas, dal
from core.database import AsyncSessionLocal

router = APIRouter(tags=["IDCardTypes"])

<<<<<<< Updated upstream
@router.get("/")
async def users():
    return {"ejemplo": "ejemplo"}
=======
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.IdCardTypeResponse)
async def create_id_card_type(id_card_type_create: schemas.IdCardTypeCreate, db: AsyncSession = Depends(get_db)):
    return await dal.IdCardTypeDAL(db).create_id_card_type(id_card_type_create)

@router.get("/", response_model=List[schemas.IdCardTypeResponse])
async def list_id_card_types(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await dal.IdCardTypeDAL(db).list_id_card_types(skip, limit)

@router.get("/{id_card_type_id}", response_model=schemas.IdCardTypeResponse)
async def get_id_card_type(id_card_type_id: int, db: AsyncSession = Depends(get_db)):
    id_card_type = await dal.IdCardTypeDAL(db).get_id_card_type(id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=404, detail="ID Card Type not found")
    return id_card_type

@router.patch("/{id_card_type_id}", response_model=schemas.IdCardTypeResponse)
async def update_id_card_type(id_card_type_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    updated = await dal.IdCardTypeDAL(db).update_id_card_type(id_card_type_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="ID Card Type not found")
    return updated

@router.delete("/{id_card_type_id}")
async def delete_id_card_type(id_card_type_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await dal.IdCardTypeDAL(db).delete_id_card_type(id_card_type_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ID Card Type not found")
    return {"deleted": deleted}
>>>>>>> Stashed changes

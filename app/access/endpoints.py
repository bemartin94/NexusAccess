from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.access import schemas, dal
from core.database import AsyncSessionLocal

router = APIRouter(tags=["Access"])

<<<<<<< Updated upstream
@router.get("/")
async def access():
    return {"ejemplo": "ejemplo"}
=======
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.AccessResponse, status_code=status.HTTP_201_CREATED)
async def create_access(access_create: schemas.AccessBase, db: AsyncSession = Depends(get_db)):
    return await dal.AccessDAL(db).create_access(access_create)

@router.get("/", response_model=List[schemas.AccessResponse])
async def list_accesses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await dal.AccessDAL(db).list_accesses(skip, limit)

@router.get("/{access_id}", response_model=schemas.AccessResponse)
async def get_access(access_id: int, db: AsyncSession = Depends(get_db)):
    access = await dal.AccessDAL(db).get_access_by_id(access_id)
    if not access:
        raise HTTPException(status_code=404, detail="Access not found")
    return access

@router.patch("/{access_id}", response_model=schemas.AccessResponse)
async def update_access(access_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    updated_access = await dal.AccessDAL(db).update_access(access_id, updates)
    if not updated_access:
        raise HTTPException(status_code=404, detail="Access not found")
    return updated_access

@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access(access_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await dal.AccessDAL(db).delete_access(access_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Access not found")
>>>>>>> Stashed changes

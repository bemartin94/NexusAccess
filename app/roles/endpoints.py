from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.roles import schemas, dal
from core.database import AsyncSessionLocal

router = APIRouter(tags=["Roles"])

<<<<<<< Updated upstream
@router.get("/")
async def roles():
    return {"ejemplo": "ejemplo"}
=======
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.RoleResponse)
async def create_role(role_create: schemas.RoleCreate, db: AsyncSession = Depends(get_db)):
    return await dal.RoleDAL(db).create_role(role_create)

@router.get("/", response_model=List[schemas.RoleResponse])
async def list_roles(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await dal.RoleDAL(db).list_roles(skip, limit)

@router.get("/{role_id}", response_model=schemas.RoleResponse)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await dal.RoleDAL(db).get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.patch("/{role_id}", response_model=schemas.RoleResponse)
async def update_role(role_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    updated = await dal.RoleDAL(db).update_role(role_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Role not found")
    return updated

@router.delete("/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await dal.RoleDAL(db).delete_role(role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"deleted": deleted}
>>>>>>> Stashed changes

from fastapi import APIRouter, Depends, HTTPException, status # Importa status
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import schemas, dal
from core.database import AsyncSessionLocal
from typing import Optional, List
from core.models import User, Role, Venue
from sqlalchemy.future import select
from app.auth import security as auth_security # <--- ¡IMPORTA EL MÓDULO DE SEGURIDAD PARA HASHEAR!

router = APIRouter(tags=["Users"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED) # Añadí status_code para ser explícito
async def create_user(
    user_in: schemas.UserCreate, # Cambié 'user' a 'user_in' para consistencia con auth/endpoints.py
    db: AsyncSession = Depends(get_db)
):
    # Opcional: Verificar si ya existe un usuario con el mismo email antes de hashear
    existing_user = await dal.UserDAL(db).get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )

    # *** PUNTO CLAVE: HASHEAR LA CONTRASEÑA AQUÍ ***
    hashed_password = auth_security.get_password_hash(user_in.password)
    
    # Crear una nueva instancia de UserCreate con la contraseña hasheada
    user_to_create = user_in.model_copy(update={"password": hashed_password})

    # Pasar la instancia con la contraseña hasheada al DAL
    return await dal.UserDAL(db).create_user(user_to_create)

@router.get("/", response_model=list[schemas.UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    return await dal.UserDAL(db).list_users()

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await dal.UserDAL(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Si 'password' es un campo que se puede actualizar, también deberías hashearlo aquí
    if user_update.password: # Solo hashear si se provee una nueva contraseña
        user_update.password = auth_security.get_password_hash(user_update.password)

    updated = await dal.UserDAL(db).update_user(user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await dal.UserDAL(db).delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": deleted}
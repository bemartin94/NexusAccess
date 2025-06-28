# app/users/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
# Importar los roles y la dependencia has_role
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR, RECEPTIONIST
from app.users.dal import UserDAL
from app.roles.dal import RoleDAL
from app.venues.dal import VenueDAL
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.venues.dal import VenueDAL
from core.models import User # Asegúrate de que User esté importado para el tipo de current_user


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["Users"]) 


# --- Gestión de Usuarios (Ahora centralizada aquí) ---
# Todos estos endpoints requieren SYSTEM_ADMINISTRATOR
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema. Requiere rol de System Administrator.
    """
    user_dal = UserDAL(db)
    role_dal = RoleDAL(db)
    
    role = await role_dal.get_role_by_id(user_data.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Role ID no válido.")
    
    if user_data.venue_id:
        venue_dal = VenueDAL(db)
        venue = await venue_dal.get_venue_by_id(user_data.venue_id)
        if not venue:
            raise HTTPException(status_code=400, detail="Venue ID no válido.")

    existing_user = await user_dal.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
    new_user = await user_dal.create_user(user_data)
    return new_user

@router.get("/", response_model=List[UserResponse],
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_all_users(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de todos los usuarios. Requiere rol de System Administrator.
    """
    user_dal = UserDAL(db)
    users = await user_dal.get_users(skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse,
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un usuario por su ID. Requiere rol de System Administrator.
    """
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user

@router.patch("/{user_id}", response_model=UserResponse,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def update_user( # Renombrado de update_user_by_admin para ser más genérico
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la información de un usuario. Requiere rol de System Administrator.
    """
    user_dal = UserDAL(db)
    
    if user_data.role_id:
        role_dal = RoleDAL(db)
        role = await role_dal.get_role_by_id(user_data.role_id)
        if not role:
            raise HTTPException(status_code=400, detail="Role ID no válido.")
    
    if user_data.venue_id:
        venue_dal = VenueDAL(db)
        venue = await venue_dal.get_venue_by_id(user_data.venue_id)
        if not venue:
            raise HTTPException(status_code=400, detail="Venue ID no válido.")

    updated_user = await user_dal.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def delete_user( # Renombrado de delete_user_by_admin
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un usuario del sistema. Requiere rol de System Administrator.
    """
    user_dal = UserDAL(db)
    success = await user_dal.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {} # Retornar un dict vacío para 204 No Content

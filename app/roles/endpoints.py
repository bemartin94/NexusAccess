# app/roles/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR # Importa el rol de administrador
from app.roles.dal import RoleDAL
from app.roles.schemas import RoleCreate, RoleResponse
from core.models import User # Para el tipo de current_user


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["Roles"]) 


# --- Gestión de Roles (Ahora centralizada aquí) ---
# Todos estos endpoints requieren SYSTEM_ADMINISTRATOR
@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo rol en el sistema. Requiere rol de System Administrator.
    """
    role_dal = RoleDAL(db)
    existing_role = await role_dal.get_role_by_name(role_data.name)
    if existing_role:
        raise HTTPException(status_code=400, detail="El rol ya existe.")
    new_role = await role_dal.create_role(role_data)
    return new_role

@router.get("/", response_model=List[RoleResponse],
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_all_roles(
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de todos los roles. Requiere rol de System Administrator.
    """
    role_dal = RoleDAL(db)
    roles = await role_dal.get_roles()
    return roles

@router.get("/{role_id}", response_model=RoleResponse,
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_role_by_id(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un rol por su ID. Requiere rol de System Administrator.
    """
    role_dal = RoleDAL(db)
    role = await role_dal.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return role

# No hay endpoint PATCH para roles en tu admin_router original, pero si lo necesitaras, lo añadirías aquí.

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un rol del sistema. Requiere rol de System Administrator.
    """
    role_dal = RoleDAL(db)
    success = await role_dal.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return {} # Retornar un dict vacío para 204 No Content

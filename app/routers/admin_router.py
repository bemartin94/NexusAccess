# app/routers/admin_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR # Importa has_role y las constantes
from app.users.dal import UserDAL
from app.roles.dal import RoleDAL
from app.venues.dal import VenueDAL
from app.id_card_types.dal import IdCardTypeDAL

from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.roles.schemas import RoleCreate, RoleResponse
from app.venues.schemas import VenueCreate, VenueUpdate, VenueResponse
from app.id_card_types.schemas import IdCardTypeCreate, IdCardTypeUpdate
from core.models import User # Para el tipo de current_user (aunque has_role ya lo asegura)

# Ahora el router depende directamente de has_role con los roles requeridos
router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])

# --- Gestión de Usuarios (Admin crea/edita cualquier usuario) ---
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    # Validar que el role_id exista
    role_dal = RoleDAL(db)
    role = await role_dal.get_role_by_id(user_data.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Role ID no válido.")
    
    # Validar que venue_id exista si se proporciona
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

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    users = await user_dal.get_users(skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return user

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_by_admin(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    # Validar role_id si se cambia
    if user_data.role_id:
        role_dal = RoleDAL(db)
        role = await role_dal.get_role_by_id(user_data.role_id)
        if not role:
            raise HTTPException(status_code=400, detail="Role ID no válido.")
    # Validar venue_id si se cambia
    if user_data.venue_id:
        venue_dal = VenueDAL(db)
        venue = await venue_dal.get_venue_by_id(user_data.venue_id)
        if not venue:
            raise HTTPException(status_code=400, detail="Venue ID no válido.")

    updated_user = await user_dal.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    success = await user_dal.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"message": "Usuario eliminado exitosamente."}

# --- Gestión de Roles (Admin) ---
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role_data: RoleCreate, db: AsyncSession = Depends(get_db)):
    role_dal = RoleDAL(db)
    existing_role = await role_dal.get_role_by_name(role_data.name)
    if existing_role:
        raise HTTPException(status_code=400, detail="El rol ya existe.")
    new_role = await role_dal.create_role(role_data)
    return new_role

@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(db: AsyncSession = Depends(get_db)):
    role_dal = RoleDAL(db)
    roles = await role_dal.get_roles()
    return roles


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role_dal = RoleDAL(db)
    success = await role_dal.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return {"message": "Rol eliminado exitosamente."}

# --- Gestión de Sedes (Admin) ---
@router.post("/venues", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(venue_data: VenueCreate, db: AsyncSession = Depends(get_db)):
    venue_dal = VenueDAL(db)
    # Opcional: Validar si main_supervisor_user_id existe y es un supervisor
    if venue_data.main_supervisor_user_id:
        user_dal = UserDAL(db)
        supervisor_user = await user_dal.get_user_by_id(venue_data.main_supervisor_user_id)
        # Aquí la validación de rol de supervisor se hace por el nombre de rol
        if not supervisor_user or (supervisor_user.role and supervisor_user.role.name not in VENUE_SUPERVISOR):
            raise HTTPException(status_code=400, detail=f"main_supervisor_user_id debe ser un usuario existente con rol de '{VENUE_SUPERVISOR[0]}'.")

    existing_venue = await venue_dal.get_venue_by_name(venue_data.name)
    if existing_venue:
        raise HTTPException(status_code=400, detail="La sede con este nombre ya existe.")
    new_venue = await venue_dal.create_venue(venue_data)
    return new_venue

@router.get("/venues", response_model=List[VenueResponse])
async def get_all_venues(db: AsyncSession = Depends(get_db)):
    venue_dal = VenueDAL(db)
    venues = await venue_dal.get_venues()
    return venues

@router.get("/venues/{venue_id}", response_model=VenueResponse)
async def get_venue_by_id(venue_id: int, db: AsyncSession = Depends(get_db)):
    venue_dal = VenueDAL(db)
    venue = await venue_dal.get_venue_by_id(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Sede no encontrada.")
    return venue

@router.patch("/venues/{venue_id}", response_model=VenueResponse)
async def update_venue(venue_id: int, venue_data: VenueUpdate, db: AsyncSession = Depends(get_db)):
    venue_dal = VenueDAL(db)
    if venue_data.main_supervisor_user_id:
        user_dal = UserDAL(db)
        supervisor_user = await user_dal.get_user_by_id(venue_data.main_supervisor_user_id)
        if not supervisor_user or (supervisor_user.role and supervisor_user.role.name not in VENUE_SUPERVISOR):
            raise HTTPException(status_code=400, detail=f"main_supervisor_user_id debe ser un usuario existente con rol de '{VENUE_SUPERVISOR[0]}'.")

    updated_venue = await venue_dal.update_venue(venue_id, venue_data)
    if not updated_venue:
        raise HTTPException(status_code=404, detail="Sede no encontrada.")
    return updated_venue

@router.delete("/venues/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(venue_id: int, db: AsyncSession = Depends(get_db)):
    venue_dal = VenueDAL(db)
    success = await venue_dal.delete_venue(venue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sede no encontrada.")
    return {"message": "Sede eliminada exitosamente."}

# --- Gestión de Tipos de Documento de Identidad (Admin) ---


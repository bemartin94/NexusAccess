# app/venues/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR # Importa roles necesarios
from app.venues.dal import VenueDAL
from app.users.dal import UserDAL # Para validar el supervisor principal
from app.venues.schemas import VenueCreate, VenueUpdate, VenueResponse
from core.models import User # Para el tipo de current_user


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["Venues"]) 


# --- Gestión de Sedes (Ahora centralizada aquí) ---
# Todos estos endpoints requieren SYSTEM_ADMINISTRATOR
@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una nueva sede en el sistema. Requiere rol de System Administrator.
    """
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

@router.get("/", response_model=List[VenueResponse],
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_all_venues( # Renombrado de get_all_venues_for_admin
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de todas las sedes. Requiere rol de System Administrator.
    """
    venue_dal = VenueDAL(db)
    venues = await venue_dal.get_venues()
    return venues

@router.get("/{venue_id}", response_model=VenueResponse,
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_venue_by_id(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una sede por su ID. Requiere rol de System Administrator.
    """
    venue_dal = VenueDAL(db)
    venue = await venue_dal.get_venue_by_id(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Sede no encontrada.")
    return venue

@router.patch("/{venue_id}", response_model=VenueResponse,
              dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def update_venue( # Renombrado de update_venue_by_admin
    venue_id: int,
    venue_data: VenueUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la información de una sede. Requiere rol de System Administrator.
    """
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

@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def delete_venue( # Renombrado de delete_venue_by_admin
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina una sede del sistema. Requiere rol de System Administrator.
    """
    venue_dal = VenueDAL(db)
    success = await venue_dal.delete_venue(venue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sede no encontrada.")
    return {} # Retornar un dict vacío para 204 No Content


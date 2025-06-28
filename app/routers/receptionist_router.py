# app/routers/receptionist_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
from app.auth.security import has_role, RECEPTIONIST # Importa has_role y la constante
from app.visitors.dal import VisitorDAL
from app.access.dal import AccessDAL
from app.id_card_types.dal import IdCardTypeDAL
from core.models import User # Para el tipo de current_user

from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse
from app.access.schemas import AccessCreate, AccessResponse

# El router ahora depende de has_role con el rol de recepcionista
router = APIRouter(prefix="/receptionist", tags=["Receptionist"], dependencies=[Depends(has_role(RECEPTIONIST))])

# --- Gestión de Visitantes (Recepcionista puede registrar/editar en su sede) ---
@router.post("/visitors", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor_by_receptionist(
    visitor_data: VisitorCreate,
    current_user: User = Depends(has_role(RECEPTIONIST)),
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    # Validar que el id_card_type_id exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    # El visitante se registra en la sede del recepcionista
    if not current_user.venue_id:
        raise HTTPException(status_code=400, detail="El recepcionista no tiene una sede asignada para registrar visitantes.")
    
    visitor_data.registration_venue_id = current_user.venue_id

    existing_visitor = await visitor_dal.get_visitor_by_id_card_number(visitor_data.id_card_number)
    if existing_visitor:
        raise HTTPException(status_code=400, detail="Un visitante con este número de documento ya está registrado.")
    
    new_visitor = await visitor_dal.create_visitor(visitor_data)
    return new_visitor

@router.get("/visitors", response_model=List[VisitorResponse])
async def get_visitors_for_receptionist_venue(
    current_user: User = Depends(has_role(RECEPTIONIST)),
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    # Filtra los visitantes registrados en la sede del recepcionista
    visitors = await visitor_dal.get_visitors(skip=skip, limit=limit)
    # Filtrar en Python. Considera añadir filtro al DAL.
    filtered_visitors = [
        v for v in visitors 
        if v.registration_venue_id == current_user.venue_id
    ]
    return filtered_visitors

@router.get("/visitors/{visitor_id}", response_model=VisitorResponse)
async def get_visitor_by_id_for_receptionist(
    visitor_id: int,
    current_user: User = Depends(has_role(RECEPTIONIST)),
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    if not visitor or visitor.registration_venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    return visitor

@router.patch("/visitors/{visitor_id}", response_model=VisitorResponse)
async def update_visitor_by_receptionist(
    visitor_id: int,
    visitor_data: VisitorUpdate,
    current_user: User = Depends(has_role(RECEPTIONIST)),
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    existing_visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    if not existing_visitor or existing_visitor.registration_venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    
    if visitor_data.id_card_type_id:
        id_card_type_dal = IdCardTypeDAL(db)
        id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_data.id_card_type_id)
        if not id_card_type:
            raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    updated_visitor = await visitor_dal.update_visitor(visitor_id, visitor_data)
    return updated_visitor


# --- Gestión de Acceso (Recepcionista puede registrar accesos de entrada y salida) ---
@router.post("/access_logs", response_model=AccessResponse, status_code=status.HTTP_201_CREATED)
async def create_access_log_by_receptionist(
    access_data: AccessCreate,
    current_user: User = Depends(has_role(RECEPTIONIST)),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db)
    visitor_dal = VisitorDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    # Validar que el visitante exista
    visitor = await visitor_dal.get_visitor_by_id(access_data.visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Validar que la sede de acceso coincida con la del recepcionista
    if access_data.venue_id != current_user.venue_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para registrar accesos en esta sede.")
    
    # Validar que el tipo de documento usado para el acceso exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(access_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad para el acceso no válido.")

    # Asignar el ID del usuario actual como quien registra el acceso
    access_data.logged_by_user_id = current_user.id
    access_data.status = "Activo" # Un nuevo acceso siempre comienza como "Activo"

    new_access_log = await access_dal.create_access_log(access_data)
    return new_access_log

@router.patch("/access_logs/{access_id}/exit", response_model=AccessResponse)
async def mark_access_exit_by_receptionist(
    access_id: int,
    current_user: User = Depends(has_role(RECEPTIONIST)),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db)
    access_log = await access_dal.get_access_log_by_id(access_id)
    
    # Asegurarse de que el log de acceso exista y pertenezca a la sede del recepcionista
    if not access_log or access_log.venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Acceso no encontrado o no pertenece a tu sede.")
    
    if access_log.status != "Activo":
         raise HTTPException(status_code=400, detail="Este acceso ya no está activo para marcar salida.")

    updated_access = await access_dal.mark_access_exit_time(access_id)
    if not updated_access:
        raise HTTPException(status_code=500, detail="Error al marcar la salida.")
    return updated_access
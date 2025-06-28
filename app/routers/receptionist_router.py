# app/routers/receptionist_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, time, timezone

from core.database import get_db
from app.auth.security import has_role, RECEPTIONIST, VENUE_SUPERVISOR, SYSTEM_ADMINISTRATOR # Importa ambos roles
from app.visitors.dal import VisitorDAL # Se mantiene por register_full_visit
from app.access.dal import AccessDAL
from app.id_card_types.dal import IdCardTypeDAL
from core.models import User, Access # Importa el modelo Access para el tipo de retorno

# Importa los esquemas de visitantes, incluyendo el **VisitCreateRequest ajustado**
from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse, VisitCreateRequest

# Importa los esquemas de acceso
from app.access.schemas import AccessCreate, AccessResponse


# Definición del Router: Ahora permite tanto a Recepcionistas como a Supervisores de Sede
router = APIRouter(
    tags=["Receptionist"], 
    dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])


# --- ENDPOINT CENTRALIZADO: Registrar Visita Completa ---
@router.post("/register_full_visit", response_model=AccessResponse, status_code=status.HTTP_201_CREATED)
async def register_full_visit(
    visit_request: VisitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])) 
):
    """
    Registra una visita completa, incluyendo la creación o búsqueda del visitante y el registro de acceso.
    """
    visitor_dal = VisitorDAL(db)
    access_dal = AccessDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    # 1. Validaciones iniciales
    # Administradores no tienen restricciones de sede aquí
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El recepcionista/supervisor no tiene una sede asignada.")
        
        if visit_request.sede != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No autorizado para registrar visitas en esta sede.")

    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visit_request.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    # 2. Buscar o crear el visitante
    existing_visitor = await visitor_dal.get_visitor_by_id_card_number(visit_request.id_card) 

    visitor_to_log = None
    if not existing_visitor:
        new_visitor_data = VisitorCreate(
            name=visit_request.name,
            last_name=visit_request.last_name,
            id_card_number=visit_request.id_card,
            phone=visit_request.phone,
            email=visit_request.email,
            picture=None,
            purpose_of_visit=None, 
            id_card_type_id=visit_request.id_card_type_id,
            # Si el usuario no es administrador, la sede de registro es la del usuario
            registration_venue_id=current_user.venue_id if current_user.role.name != SYSTEM_ADMINISTRATOR[0] else visit_request.sede # Admin puede especificar sede
        )
        new_visitor = await visitor_dal.create_visitor(new_visitor_data)
        visitor_to_log = new_visitor
    else:
        visitor_to_log = existing_visitor
        update_visitor_data = VisitorUpdate(
            name=visit_request.name,
            last_name=visit_request.last_name,
            phone=visit_request.phone,
            email=visit_request.email,
        )
        await visitor_dal.update_visitor(existing_visitor.id, update_visitor_data)
        visitor_to_log = await visitor_dal.get_visitor_by_id(existing_visitor.id)


    # 3. Crear el registro de acceso
    entry_datetime = datetime.combine(visit_request.fecha, visit_request.hora_ing).astimezone(timezone.utc)


    access_create_data = AccessCreate(
        visitor_id=visitor_to_log.id,
        venue_id=visit_request.sede,
        id_card_type_id=visit_request.id_card_type_id,
        id_card_number_at_access=visit_request.id_card,
        logged_by_user_id=current_user.id,
        access_reason=visit_request.reason_visit,
        status="Activo"
    )

    new_access_log = await access_dal.create_access_log(access_create_data, entry_time=entry_datetime) 
    
    return new_access_log

# --- Gestión de Visitantes - ELIMINADO de aquí (movido a app/visitors/endpoints.py) ---
# @router.post("/visitors", ...)
# @router.get("/visitors", ...)
# @router.get("/visitors/{visitor_id}", ...)
# @router.patch("/visitors/{visitor_id}", ...)


# --- Gestión de Acceso (Estos se moverán al access_router.py en el siguiente paso) ---
@router.post("/access_logs", response_model=AccessResponse, status_code=status.HTTP_201_CREATED)
async def create_access_log_by_receptionist(
    access_data: AccessCreate,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """Crea un registro de acceso (entrada) para un visitante existente."""
    access_dal = AccessDAL(db)
    visitor_dal = VisitorDAL(db) # Se necesita para validar que el visitante exista
    id_card_type_dal = IdCardTypeDAL(db)

    # Validar que el visitante exista
    visitor = await visitor_dal.get_visitor_by_id(access_data.visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Validar que la sede de acceso coincida con la del recepcionista/supervisor si no es admin
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if access_data.venue_id != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para registrar accesos en esta sede.")
    
    # Validar que el tipo de documento usado para el acceso exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(access_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad para el acceso no válido.")

    access_data.logged_by_user_id = current_user.id
    access_data.status = "Activo" # Un nuevo acceso siempre comienza como "Activo"

    # Este endpoint create_access_log no recibe entry_time, debería ser manejado por AccessCreate o DAL
    new_access_log = await access_dal.create_access_log(access_data, entry_time=datetime.now(timezone.utc)) 
    return new_access_log

@router.patch("/access_logs/{access_id}/exit", response_model=AccessResponse)
async def mark_access_exit_by_receptionist(
    access_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """Marca la salida de un registro de acceso existente."""
    access_dal = AccessDAL(db)
    access_log = await access_dal.get_access_record_by_id(access_id)
    
    if not access_log:
        raise HTTPException(status_code=404, detail="Acceso no encontrado.")
    
    # Asegurarse de que el log de acceso exista y pertenezca a la sede del usuario si no es administrador
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or access_log.venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Acceso no encontrado o no pertenece a tu sede.")
    
    if access_log.status != "Activo":
        raise HTTPException(status_code=400, detail="Este acceso ya no está activo para marcar salida.")

    updated_access = await access_dal.mark_access_exit_time(access_id)
    if not updated_access:
        raise HTTPException(status_code=500, detail="Error al marcar la salida.")
    return updated_access

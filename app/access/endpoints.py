# app/access/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, timezone 

from core.database import get_db
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR, RECEPTIONIST
from app.visitors.dal import VisitorDAL 
from app.access.dal import AccessDAL 
from app.id_card_types.dal import IdCardTypeDAL 
from app.access.schemas import AccessCreate, AccessUpdate, AccessResponse
from app.visitors.schemas import VisitCreateRequest, VisitorCreate, VisitorUpdate 
from core.models import User, Access 


router = APIRouter(tags=["Access Management"]) 


# --- Endpoint Principal: Registrar Visita Completa ---
@router.post("/register_full_visit", response_model=AccessResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def register_full_visit(
    visit_request: VisitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])) 
):
    visitor_dal = VisitorDAL(db)
    access_dal = AccessDAL(db) 
    id_card_type_dal = IdCardTypeDAL(db)

    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para registrar visitas.")
        
        if visit_request.sede != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No autorizado para registrar visitas en esta sede.")
    
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visit_request.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

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
            registration_venue_id=current_user.venue_id if current_user.role.name != SYSTEM_ADMINISTRATOR[0] else visit_request.sede
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


# --- Otros Endpoints de Gestión de Acceso ---

@router.post("/", response_model=AccessResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def create_access_log( 
    access_data: AccessCreate,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db) 
    visitor_dal = VisitorDAL(db) 
    id_card_type_dal = IdCardTypeDAL(db)

    visitor = await visitor_dal.get_visitor_by_id(access_data.visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if access_data.venue_id != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para registrar accesos en esta sede.")
    
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(access_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad para el acceso no válido.")

    access_data.logged_by_user_id = current_user.id
    access_data.status = "Activo" 

    new_access_log = await access_dal.create_access_log(access_data, entry_time=datetime.now(timezone.utc)) 
    return new_access_log


@router.get("/", response_model=List[AccessResponse],
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_all_access_records( 
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    skip: int = 0, limit: int = 100,
    date_filter: Optional[date] = Query(None, description="Filtrar por fecha (YYYY-MM-DD)"),
    id_card_filter: Optional[str] = Query(None, description="Filtrar por número de documento de identidad"),
    venue_id: Optional[int] = Query(None, description="Filtrar por ID de sede (solo para Administradores)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de registros de acceso.
    Administradores ven todos los registros y pueden filtrar por sede.
    Recepcionistas/Supervisores ven registros de su sede asignada.
    """
    access_dal = AccessDAL(db) 
    
    # DEBUG: Imprime el filtro de fecha recibido para verificar
    print(f"Backend: Received date_filter: {date_filter} (type: {type(date_filter)})")
    print(f"Backend: Received id_card_filter: {id_card_filter} (type: {type(id_card_filter)})")
    print(f"Backend: Current user role: {current_user.role.name}") # <--- ¡NUEVA LÍNEA CLAVE!
    print(f"Backend: Current user venue_id: {current_user.venue_id}") 

    venue_id_filter = None
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para ver registros de acceso.")
        venue_id_filter = current_user.venue_id
        if venue_id is not None and venue_id != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver registros de acceso de otras sedes.")
    else:
        venue_id_filter = venue_id
    
    print(f"Backend: Final venue_id_filter passed to DAL: {venue_id_filter}") # <--- ¡NUEVA LÍNEA CLAVE!

    access_records = await access_dal.get_access_records(
        skip=skip,
        limit=limit,
        date_filter=date_filter,
        id_card_filter=id_card_filter,
        venue_id=venue_id_filter
    )
    
    # DEBUG: Imprime los registros encontrados ANTES de devolverlos
    print(f"Backend: Found {len(access_records)} records for filters.")
    if len(access_records) > 0:
        print("Backend: First record entry_time:", access_records[0].entry_time)
        print("Backend: First record venue_id:", access_records[0].venue_id)
    
    return access_records


@router.get("/{access_id}", response_model=AccessResponse,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_access_record_by_id( 
    access_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db) 
    access_log = await access_dal.get_access_record_by_id(access_id)
    
    if not access_log:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or access_log.venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Registro de acceso no encontrado o no pertenece a tu sede.")
    
    return access_log


@router.patch("/{access_id}", response_model=AccessResponse,
             dependencies=[Depends(has_role([SYSTEM_ADMINISTRATOR[0]]))]) 
async def update_access_record(
    access_id: int,
    access_data: AccessUpdate,
    current_user: User = Depends(has_role([SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db) 
    updated_access = await access_dal.update_access(access_id, access_data)
    if not updated_access:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    return updated_access

@router.patch("/{access_id}/exit", response_model=AccessResponse,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def mark_access_exit( 
    access_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db) 
    access_log = await access_dal.get_access_record_by_id(access_id)
    
    if not access_log:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or access_log.venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Registro de acceso no encontrado o no pertenece a tu sede.")
    
    if access_log.status != "Activo":
        raise HTTPException(status_code=400, detail="Este acceso ya no está activo para marcar salida.")

    updated_access = await access_dal.mark_access_exit_time(access_id)
    if not updated_access:
        raise HTTPException(status_code=500, detail="Error al marcar la salida.")
    return updated_access


@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))]) 
async def delete_access_record( 
    access_id: int,
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db) 
    success = await access_dal.delete_access(access_id)
    if not success:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    return {} 

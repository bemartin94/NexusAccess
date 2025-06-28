# app/access/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, timezone # Asegúrate de que timezone esté importado

from core.database import get_db
# Importar los roles y la dependencia has_role
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR, RECEPTIONIST
from app.visitors.dal import VisitorDAL # Se necesita para register_full_visit
from app.access.dal import AccessDAL
from app.id_card_types.dal import IdCardTypeDAL # Para validaciones
from app.access.schemas import AccessCreate, AccessUpdate, AccessResponse
from app.visitors.schemas import VisitCreateRequest, VisitorCreate, VisitorUpdate # Para register_full_visit
from core.models import User, Access # Para el tipo de current_user y modelo de acceso


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["Access Management"]) 


# --- Endpoint Principal: Registrar Visita Completa (anteriormente en receptionist_router) ---
@router.post("/register_full_visit", response_model=AccessResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def register_full_visit(
    visit_request: VisitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])) 
):
    """
    Registra una visita completa, incluyendo la creación o búsqueda del visitante y el registro de acceso.
    Accesible por Recepcionistas, Supervisores de Sede y Administradores del Sistema.
    Recepcionistas/Supervisores solo pueden registrar en su sede. Administradores en cualquier sede.
    """
    visitor_dal = VisitorDAL(db)
    access_dal = AccessDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    # 1. Validaciones iniciales de sede (para no-administradores)
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para registrar visitas.")
        
        if visit_request.sede != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No autorizado para registrar visitas en esta sede.")
    
    # Validar tipo de documento
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
        # Necesitamos el objeto visitante actualizado con todas sus propiedades (incluidas las que no se actualizaron)
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


# --- Otros Endpoints de Gestión de Acceso ---

@router.post("/", response_model=AccessResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def create_access_log( # Renombrado de create_access_log_by_receptionist
    access_data: AccessCreate,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un registro de acceso (entrada) para un visitante existente.
    Accesible por Recepcionistas, Supervisores de Sede y Administradores del Sistema.
    Recepcionistas/Supervisores solo pueden registrar en su sede. Administradores en cualquier sede.
    """
    access_dal = AccessDAL(db)
    visitor_dal = VisitorDAL(db) 
    id_card_type_dal = IdCardTypeDAL(db)

    # Validar que el visitante exista
    visitor = await visitor_dal.get_visitor_by_id(access_data.visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Validar que la sede de acceso coincida con la del usuario si no es administrador
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if access_data.venue_id != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para registrar accesos en esta sede.")
    
    # Validar que el tipo de documento usado para el acceso exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(access_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad para el acceso no válido.")

    access_data.logged_by_user_id = current_user.id
    access_data.status = "Activo" # Un nuevo acceso siempre comienza como "Activo"

    new_access_log = await access_dal.create_access_log(access_data, entry_time=datetime.now(timezone.utc)) 
    return new_access_log


@router.get("/", response_model=List[AccessResponse],
            dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_all_access_records( # Renombrado de get_access_logs_for_supervisor_venue
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
    
    venue_id_filter = None
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para ver registros de acceso.")
        venue_id_filter = current_user.venue_id
        # Ignorar venue_id del query si no es admin, ya que solo pueden ver su propia sede
        if venue_id is not None and venue_id != current_user.venue_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver registros de acceso de otras sedes.")
    else:
        # Si es administrador, puede usar el venue_id del query para filtrar
        venue_id_filter = venue_id

    access_records = await access_dal.get_access_records(
        skip=skip,
        limit=limit,
        date_filter=date_filter,
        id_card_filter=id_card_filter,
        venue_id=venue_id_filter
    )
    return access_records


@router.get("/{access_id}", response_model=AccessResponse,
            dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_access_record_by_id( # Renombrado de get_access_record_by_id_receptionist
    access_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un registro de acceso por su ID.
    Administradores pueden ver cualquier registro. Recepcionistas/Supervisores solo registros de su sede.
    """
    access_dal = AccessDAL(db)
    access_log = await access_dal.get_access_record_by_id(access_id)
    
    if not access_log:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    
    # Si el usuario no es administrador, verifica que el registro pertenezca a su sede
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or access_log.venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Registro de acceso no encontrado o no pertenece a tu sede.")
    
    return access_log


@router.patch("/{access_id}", response_model=AccessResponse,
               dependencies=[Depends(has_role([SYSTEM_ADMINISTRATOR[0]]))]) # SOLO ADMIN por ahora
async def update_access_record( # Renombrado de update_access_by_admin (si existía)
    access_id: int,
    access_data: AccessUpdate,
    current_user: User = Depends(has_role([SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la información de un registro de acceso. Requiere rol de System Administrator.
    """
    access_dal = AccessDAL(db)
    updated_access = await access_dal.update_access(access_id, access_data)
    if not updated_access:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    return updated_access

@router.patch("/{access_id}/exit", response_model=AccessResponse,
               dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def mark_access_exit( # Renombrado de mark_access_exit_by_receptionist o by_supervisor
    access_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Marca la salida de un registro de acceso existente.
    Administradores pueden marcar cualquier salida. Recepcionistas/Supervisores solo registros de su sede.
    """
    access_dal = AccessDAL(db)
    access_log = await access_dal.get_access_record_by_id(access_id)
    
    if not access_log:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    
    # Si el usuario no es administrador, verifica que el registro pertenezca a su sede
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
                dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))]) # SOLO ADMIN por ahora
async def delete_access_record( # Renombrado de delete_access_by_admin (si existía)
    access_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un registro de acceso. Requiere rol de System Administrator.
    """
    access_dal = AccessDAL(db)
    success = await access_dal.delete_access(access_id)
    if not success:
        raise HTTPException(status_code=404, detail="Registro de acceso no encontrado.")
    return {} # Retornar un dict vacío para 204 No Content

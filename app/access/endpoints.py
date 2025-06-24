# app/access/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, time # Asegúrate de importar 'time'

from core.database import get_db
from app.auth.security import get_current_active_user

# --- Importaciones de esquemas y DALs ---
from app.access.schemas import AccessResponse, AccessUpdate, AccessCreate, VisitCreateRequest
from app.access.dal import AccessDAL # Importación añadida
from app.visitors.dal import VisitorDAL
from app.visitors.schemas import VisitorCreate
from app.users.schemas import UserResponse # Para el tipo de 'current_user'

# --- Router sin prefijo, asumiendo que app.main.py lo manejará ---
router = APIRouter(tags=["Access Management"]) 


@router.post("/register_visit", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Registrar visita completa")
async def register_complete_visit(
    visit_request: VisitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Registra una visita completa, incluyendo la creación o búsqueda del visitante y el registro de acceso.
    """
    visitor_dal = VisitorDAL(db)
    access_dal = AccessDAL(db)

    # 1. Buscar o crear el visitante
    existing_visitor = await visitor_dal.get_visitor_by_id_card(visit_request.id_card)

    visitor_id = None
    if existing_visitor:
        visitor_id = existing_visitor.id
        # Opcional: Actualizar datos del visitante existente si es necesario
    else:
        new_visitor_data = VisitorCreate(
            name=visit_request.name,
            last_name=visit_request.last_name,
            id_card=visit_request.id_card,
            email=visit_request.email,
            phone=visit_request.phone,
            id_card_type_id=visit_request.id_card_type_id,
            supervisor_id=current_user.id,
            venue_id=current_user.venue_id
        )
        new_visitor = await visitor_dal.create_visitor(new_visitor_data)
        visitor_id = new_visitor.id

    # 2. Crear el registro de acceso
    entry_datetime = datetime.combine(visit_request.fecha, visit_request.hora_ing)

    access_data = AccessCreate(
        venue_id=current_user.venue_id,
        id_card_type_id=visit_request.id_card_type_id,
        visitor_id=visitor_id,
        supervisor_id=current_user.id,
        access_reason=visit_request.reason_visit,
        department=None, 
        is_recurrent=False,
        status="enabled"
    )
    new_access = await access_dal.create_access(access_data, entry_datetime)

    return {"message": "Visita registrada exitosamente", "access_id": new_access.id}


@router.get(
    "/",
    response_model=List[AccessResponse],
    summary="Listar todos los registros de acceso",
    description="Permite listar y filtrar los registros de acceso en el sistema por fecha y/o número de documento."
)
async def list_accesses_route(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a devolver"),
    date_filter: Optional[date] = Query(None, description="Filtrar por fecha de entrada (formato YYYY-MM-DD)"),
    id_card_filter: Optional[str] = Query(None, description="Filtrar por número de documento del visitante (búsqueda parcial)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Obtiene una lista de registros de acceso, con filtros y paginación,
    para la sede del usuario autenticado.
    """
    access_dal = AccessDAL(db)
    
    user_venue_id = current_user.venue_id 
    
    access_records = await access_dal.get_access_records(
        date_filter=date_filter,
        id_card_filter=id_card_filter,
        venue_id=user_venue_id,
        skip=skip,
        limit=limit
    )
    print (access_records)
    return access_records


@router.get("/{access_id}", response_model=AccessResponse, summary="Obtener registro de acceso por ID")
async def get_access_by_id_route(
    access_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Obtiene un registro de acceso específico por su ID, validando permisos.
    """
    access_dal = AccessDAL(db)
    access_record = await access_dal.get_access_record_by_id(access_id)
    
    if not access_record or access_record.venue_id != current_user.venue_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acceso no encontrado o no autorizado")
    return access_record


@router.patch("/{access_id}", response_model=AccessResponse, summary="Actualizar registro de acceso")
async def update_access_route(
    access_id: int,
    access_update: AccessUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Actualiza campos específicos de un registro de acceso (ej. hora de salida).
    """
    access_dal = AccessDAL(db)
    existing_access = await access_dal.get_access_record_by_id(access_id)
    if not existing_access or existing_access.venue_id != current_user.venue_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acceso no encontrado o no autorizado")
    
    updated_access = await access_dal.update_access(access_id, access_update)
    return updated_access


@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar registro de acceso")
async def delete_access_route(
    access_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Elimina un registro de acceso existente.
    """
    access_dal = AccessDAL(db)
    existing_access = await access_dal.get_access_record_by_id(access_id)
    if not existing_access or existing_access.venue_id != current_user.venue_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acceso no encontrado o no autorizado")
        
    await access_dal.delete_access(access_id)
    return {"message": "Registro de acceso eliminado exitosamente"}

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
from app.auth.security import has_role, VENUE_SUPERVISOR 
from app.visitors.dal import VisitorDAL
from app.access.dal import AccessDAL
from app.id_card_types.dal import IdCardTypeDAL
from core.models import User 

from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse
from app.access.schemas import AccessCreate, AccessUpdate, AccessResponse

router = APIRouter(prefix="/supervisor", tags=["Supervisor"], dependencies=[Depends(has_role(VENUE_SUPERVISOR))])

# --- Gestión de Visitantes (Supervisor puede registrar/editar en su sede) ---
@router.post("/visitors", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor_by_supervisor(
    visitor_data: VisitorCreate,
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)), # La dependencia ya asegura el rol
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)
    
    # Validar que el id_card_type_id exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    # El visitante se registra en la sede del supervisor
    if not current_user.venue_id:
        raise HTTPException(status_code=400, detail="El supervisor no tiene una sede asignada para registrar visitantes.")
    
    visitor_data.registration_venue_id = current_user.venue_id

    existing_visitor = await visitor_dal.get_visitor_by_id_card_number(visitor_data.id_card_number)
    if existing_visitor:
        raise HTTPException(status_code=400, detail="Un visitante con este número de documento ya está registrado.")
    
    new_visitor = await visitor_dal.create_visitor(visitor_data)
    return new_visitor

@router.get("/visitors", response_model=List[VisitorResponse])
async def get_visitors_for_supervisor_venue(
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    # Filtra los visitantes registrados en la sede del supervisor
    # Idealmente, el DAL debería tener un método get_visitors_by_venue_id
    visitors = await visitor_dal.get_visitors(skip=skip, limit=limit)
    filtered_visitors = [
        v for v in visitors 
        if v.registration_venue_id == current_user.venue_id
    ]
    return filtered_visitors

@router.get("/visitors/{visitor_id}", response_model=VisitorResponse)
async def get_visitor_by_id_for_supervisor(
    visitor_id: int,
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    if not visitor or visitor.registration_venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    return visitor

@router.patch("/visitors/{visitor_id}", response_model=VisitorResponse)
async def update_visitor_by_supervisor(
    visitor_id: int,
    visitor_data: VisitorUpdate,
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
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

@router.delete("/visitors/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visitor_by_supervisor(
    visitor_id: int,
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    if not visitor or visitor.registration_venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    
    success = await visitor_dal.delete_visitor(visitor_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar el visitante.")
    return {"message": "Visitante eliminado exitosamente."}

# --- Gestión de Acceso (Supervisor puede ver/cerrar accesos en su sede) ---
@router.get("/access_logs", response_model=List[AccessResponse])
async def get_access_logs_for_supervisor_venue(
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
    skip: int = 0, limit: int = 100,
    visitor_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db)
    # Un supervisor solo puede ver los logs de su propia sede
    access_logs = await access_dal.get_access_logs(
        skip=skip,
        limit=limit,
        venue_id=current_user.venue_id, # Filtro por la sede del supervisor
        visitor_id=visitor_id,
        status=status_filter
    )
    return access_logs

@router.patch("/access_logs/{access_id}/exit", response_model=AccessResponse)
async def mark_access_exit_by_supervisor(
    access_id: int,
    current_user: User = Depends(has_role(VENUE_SUPERVISOR)),
    db: AsyncSession = Depends(get_db)
):
    access_dal = AccessDAL(db)
    access_log = await access_dal.get_access_log_by_id(access_id)
    
    if not access_log or access_log.venue_id != current_user.venue_id:
        raise HTTPException(status_code=404, detail="Acceso no encontrado o no pertenece a tu sede.")
    
    if access_log.status != "Activo":
         raise HTTPException(status_code=400, detail="Este acceso ya no está activo para marcar salida.")

    updated_access = await access_dal.mark_access_exit_time(access_id)
    if not updated_access:
        raise HTTPException(status_code=500, detail="Error al marcar la salida.")
    return updated_access
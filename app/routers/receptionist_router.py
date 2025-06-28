# app/routers/receptionist_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, datetime, time, timezone # Asegúrate de que timezone esté importado

from core.database import get_db
from app.auth.security import has_role, RECEPTIONIST
from app.visitors.dal import VisitorDAL
from app.access.dal import AccessDAL
from app.id_card_types.dal import IdCardTypeDAL
from core.models import User, Access

from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse, VisitCreateRequest
from app.access.schemas import AccessCreate, AccessResponse


router = APIRouter(tags=["Receptionist"], dependencies=[Depends(has_role(RECEPTIONIST))])


@router.post("/register_full_visit", response_model=AccessResponse, status_code=status.HTTP_201_CREATED)
async def register_full_visit(
    visit_request: VisitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_role(RECEPTIONIST))
):
    """
    Registra una visita completa, incluyendo la creación o búsqueda del visitante y el registro de acceso.
    """
    visitor_dal = VisitorDAL(db)
    access_dal = AccessDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    # 1. Validaciones iniciales
    if not current_user.venue_id:
        raise HTTPException(status_code=400, detail="El recepcionista no tiene una sede asignada.")
    
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
            registration_venue_id=current_user.venue_id
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
    # Volvemos a calcular entry_datetime para pasarlo al DAL
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

    # CAMBIO CLAVE AQUÍ: Volver a pasar 'entry_time' al DAL
    new_access_log = await access_dal.create_access_log(access_create_data, entry_time=entry_datetime) 
    
    return new_access_log

# ... (El resto de tu código del router permanece igual) ...

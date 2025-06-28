# app/visitors/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
# Importar los roles y la dependencia has_role
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR, VENUE_SUPERVISOR, RECEPTIONIST
from app.visitors.dal import VisitorDAL
from app.id_card_types.dal import IdCardTypeDAL # Para validar el tipo de documento
from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse
from core.models import User # Para el tipo de current_user


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["Visitors"]) 


# --- Gestión de Visitantes (Ahora centralizada aquí) ---

@router.post("/", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def create_visitor( # Renombrado de create_visitor_by_receptionist_separate o by_supervisor
    visitor_data: VisitorCreate,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo visitante. Accesible por Recepcionistas, Supervisores de Sede y Administradores del Sistema.
    Recepcionistas y Supervisores solo pueden registrar visitantes para su sede asignada.
    Administradores pueden registrar en cualquier sede.
    """
    visitor_dal = VisitorDAL(db)
    id_card_type_dal = IdCardTypeDAL(db)

    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_data.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    # Si el usuario no es un administrador, debe tener una sede asignada y el registro debe ser en esa sede.
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para registrar visitantes.")
        # Asignar la sede de registro del visitante a la sede del usuario actual
        visitor_data.registration_venue_id = current_user.venue_id
    # Si es administrador, venue_id puede venir en visitor_data o ser None
    # Asegúrate de que visitor_data.registration_venue_id sea validado si viene de un admin.
    
    existing_visitor = await visitor_dal.get_visitor_by_id_card_number(visitor_data.id_card_number)
    if existing_visitor:
        raise HTTPException(status_code=400, detail="Un visitante con este número de documento ya está registrado.")
    
    new_visitor = await visitor_dal.create_visitor(visitor_data)
    return new_visitor


@router.get("/", response_model=List[VisitorResponse],
            dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_all_visitors( # Renombrado de get_visitors_for_receptionist_venue o get_visitors_for_supervisor_venue
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    skip: int = 0, limit: int = 100,
    search_query: Optional[str] = Query(None, description="Buscar por nombre, apellido, documento o email"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de visitantes.
    Administradores ven todos los visitantes. Recepcionistas/Supervisores ven visitantes de su sede.
    """
    visitor_dal = VisitorDAL(db)
    
    venue_id_filter = None
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id:
            raise HTTPException(status_code=400, detail="El usuario no tiene una sede asignada para ver visitantes.")
        venue_id_filter = current_user.venue_id
        
    visitors = await visitor_dal.get_visitors(
        skip=skip,
        limit=limit,
        registration_venue_id=venue_id_filter, # Se filtra por sede si no es admin
        search_query=search_query # Se añade la búsqueda
    )
    return visitors


@router.get("/{visitor_id}", response_model=VisitorResponse,
            dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def get_visitor_by_id( # Renombrado de get_visitor_by_id_for_receptionist o by_supervisor
    visitor_id: int,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un visitante por su ID.
    Administradores pueden ver cualquier visitante. Recepcionistas/Supervisores solo visitantes de su sede.
    """
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Si el usuario no es administrador, verifica que el visitante pertenezca a su sede
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or visitor.registration_venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    
    return visitor


@router.patch("/{visitor_id}", response_model=VisitorResponse,
               dependencies=[Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def update_visitor( # Renombrado de update_visitor_by_receptionist o by_supervisor
    visitor_id: int,
    visitor_data: VisitorUpdate,
    current_user: User = Depends(has_role([RECEPTIONIST[0], VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la información de un visitante.
    Administradores pueden actualizar cualquier visitante. Recepcionistas/Supervisores solo visitantes de su sede.
    """
    visitor_dal = VisitorDAL(db)
    existing_visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    
    if not existing_visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Si el usuario no es administrador, verifica que el visitante pertenezca a su sede
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or existing_visitor.registration_venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")
    
    # Validar el tipo de documento de identidad si se está actualizando
    if visitor_data.id_card_type_id:
        id_card_type_dal = IdCardTypeDAL(db)
        id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_data.id_card_type_id)
        if not id_card_type:
            raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    updated_visitor = await visitor_dal.update_visitor(visitor_id, visitor_data)
    return updated_visitor


@router.delete("/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(has_role([VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]]))])
async def delete_visitor( # Renombrado de delete_visitor_by_supervisor
    visitor_id: int,
    current_user: User = Depends(has_role([VENUE_SUPERVISOR[0], SYSTEM_ADMINISTRATOR[0]])),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un visitante del sistema. Requiere rol de Supervisor de Sede o Administrador del Sistema.
    Supervisores solo pueden eliminar visitantes de su sede.
    """
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)

    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    
    # Si el usuario no es administrador, verifica que el visitante pertenezca a su sede
    if current_user.role.name != SYSTEM_ADMINISTRATOR[0]:
        if not current_user.venue_id or visitor.registration_venue_id != current_user.venue_id:
            raise HTTPException(status_code=404, detail="Visitante no encontrado o no pertenece a tu sede.")

    success = await visitor_dal.delete_visitor(visitor_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar el visitante.")
    return {}

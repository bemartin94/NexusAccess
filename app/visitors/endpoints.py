from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Necesario para consultas asíncronas
from typing import List
from datetime import datetime # Importar datetime para combinar fecha y hora

from core.database import AsyncSessionLocal

# Importa tus modelos directamente desde core.models
from core.models import Visitor, Access, AccessTime, User, Venue, Supervisor, IdCardType # Asegúrate de que estos modelos estén definidos en core/models.py

# Importa los esquemas de visitantes, incluyendo el nuevo VisitCreateRequest
from app.visitors.schemas import VisitorCreate, VisitorResponse, VisitorUpdate, VisitCreateRequest

# Importa el DAL de visitantes
from app.visitors.dal import VisitorDAL

# Importa esquemas para Access (los modelos ya vienen de core.models)
from app.access.schemas import AccessCreate, AccessResponse # Usado en la lógica, pero no como request body principal aquí

# Importar seguridad y el esquema User para obtener el usuario actual
from app.auth.security import get_current_active_user
from app.users.schemas import UserResponse # Asumo que tienes un UserResponse schema para el usuario autenticado

# Inicializa el APIRouter
router = APIRouter(tags=["Visitors"])

# Dependencia para obtener la sesión de la base de datos
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- NUEVO ENDPOINT PARA REGISTRAR UNA VISITA COMPLETA ---
# Este endpoint maneja la creación de un visitante (si no existe) y el registro de su acceso
@router.post("/register_visit", response_model=dict, operation_id="register_complete_visit")
async def register_complete_visit(
    visit_request: VisitCreateRequest, # Utiliza el esquema combinado que creamos
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user) # Requiere autenticación
):
    # Validaciones de seguridad: asegurar que el usuario autenticado tiene permisos
    # para registrar en la sede y como supervisor especificados.
    if visit_request.supervisor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para registrar visitas para otro supervisor."
        )
    # Suponiendo que 'current_user' tiene un atributo 'venue_id'
    if hasattr(current_user, 'venue_id') and visit_request.sede != current_user.venue_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para registrar visitas en esta sede."
        )

    # 1. Buscar o crear el visitante
    visitor_dal = VisitorDAL(db)
    existing_visitor = await visitor_dal.get_by_id_card(visit_request.id_card)

    if not existing_visitor:
        # Si el visitante no existe, se crea uno nuevo
        visitor_data = VisitorCreate(
            name=visit_request.name,
            last_name=visit_request.last_name,
            id_card=visit_request.id_card,
            phone=visit_request.phone,
            email=visit_request.email,
            id_card_type_id=visit_request.id_card_type_id,
            supervisor_id=visit_request.supervisor_id,
            venue_id=visit_request.sede
        )
        new_visitor = await visitor_dal.create_visitor(visitor_data)
        visitor_id = new_visitor.id
    else:
        # Si el visitante ya existe, se usa su ID.
        # Opcional: Aquí podrías implementar lógica para actualizar campos del visitante
        # si los datos de la solicitud difieren de los existentes (ej. email, teléfono).
        visitor_id = existing_visitor.id

    # 2. Crear el registro de acceso (tabla 'accesses')
    # Los campos aquí deben coincidir con tu modelo Access en core/models.py
    access_create_data = {
        "visitor_id": visitor_id,
        "venue_id": visit_request.sede,
        "supervisor_id": visit_request.supervisor_id,
        "access_reason": visit_request.reason_visit, # Usa 'access_reason' como en tu modelo
        "id_card_type_id": visit_request.id_card_type_id,
        "status": "enabled" # Estado por defecto al crear el acceso
    }

    # Crea una instancia del modelo Access.
    db_access = Access(**access_create_data)

    try:
        db.add(db_access)
        await db.flush() # Importante: db.flush() para que db_access.id esté disponible

        # 3. Crear el registro de tiempo de acceso (tabla 'access_times')
        # Combina la fecha y hora del frontend en un solo objeto datetime
        combined_entry_datetime = datetime.combine(visit_request.fecha, visit_request.hora_ing)

        db_access_time = AccessTime(
            access_id=db_access.id, # Vincula con el Access recién creado
            access_date=combined_entry_datetime,
            exit_date=None # La fecha de salida es nula inicialmente
        )
        db.add(db_access_time)

        await db.commit() # Confirma todas las operaciones en la base de datos
        await db.refresh(db_access) # Refresca los objetos para obtener sus IDs y relaciones
        await db.refresh(db_access_time)

    except Exception as e:
        await db.rollback() # Si algo falla, se revierte la transacción
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la visita completa: {e}"
        )

    return {
        "message": "Visita registrada con éxito",
        "visitor_id": visitor_id,
        "access_id": db_access.id,
        "access_time_id": db_access_time.id
    }

# --- ENDPOINTS EXISTENTES PARA CRUD INDIVIDUAL DE VISITANTES ---
# (Estos son los que ya tenías y que no están directamente relacionados con el nuevo flujo de registro de visita completa)

# El endpoint POST "/" original si lo sigues usando para crear solo visitantes
# @router.post("/", response_model=VisitorResponse, operation_id="create_visitor")
# async def create_visitor(
#     visitor_in: VisitorCreate,
#     db: AsyncSession = Depends(get_db),
#     current_user: UserResponse = Depends(get_current_user)
# ):
#     return await VisitorDAL(db).create_visitor(visitor_in)


@router.get("/{visitor_id}", response_model=VisitorResponse, operation_id="read_visitor")
async def read_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    visitor = await VisitorDAL(db).get_by_id(visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor

@router.put("/{visitor_id}", response_model=VisitorResponse, operation_id="update_visitor")
async def update_visitor(
    visitor_id: int,
    visitor_in: VisitorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    visitor = await VisitorDAL(db).get_by_id(visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    updated_visitor = await VisitorDAL(db).update_visitor(visitor_id, visitor_in)
    if not updated_visitor:
        raise HTTPException(status_code=404, detail="Visitor not found or no changes made")
    return updated_visitor

@router.delete("/{visitor_id}", response_model=dict, operation_id="delete_visitor")
async def delete_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    dal = VisitorDAL(db)
    deleted = await dal.delete(visitor_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return {"message": "Visitor deleted successfully"}
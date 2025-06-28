# app/id_card_types/endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
from app.auth.security import has_role, SYSTEM_ADMINISTRATOR # Importa el rol de administrador
from app.id_card_types.dal import IdCardTypeDAL
from app.id_card_types.schemas import IdCardTypeCreate, IdCardTypeUpdate, IdCardTypeResponse
from core.models import User # Para el tipo de current_user


# Definición del Router: ¡SIN PREFIJO AQUÍ! El prefijo se define en main.py
router = APIRouter(tags=["IDCardTypes"]) 


# --- Gestión de Tipos de Documento de Identidad (Ahora centralizada aquí) ---
# Los endpoints CRUD requieren SYSTEM_ADMINISTRATOR

@router.post("/", response_model=IdCardTypeResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def create_id_card_type(
    id_card_type_data: IdCardTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo tipo de documento de identidad. Requiere rol de System Administrator.
    """
    id_card_type_dal = IdCardTypeDAL(db)
    existing_type = await id_card_type_dal.get_id_card_type_by_name(id_card_type_data.name)
    if existing_type:
        raise HTTPException(status_code=400, detail="Este tipo de documento ya existe.")
    new_type = await id_card_type_dal.create_id_card_type(id_card_type_data)
    return new_type

@router.get("/", response_model=List[IdCardTypeResponse],
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))]) # Este GET ahora está protegido
async def get_all_id_card_types( # Renombrado de get_all_id_card_types_admin para ser genérico
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista de todos los tipos de documentos de identidad. Requiere rol de System Administrator.
    """
    id_card_type_dal = IdCardTypeDAL(db)
    types = await id_card_type_dal.get_id_card_types()
    return types

@router.get("/{id_card_type_id}", response_model=IdCardTypeResponse,
            dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def get_id_card_type_by_id(
    id_card_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene un tipo de documento de identidad por su ID. Requiere rol de System Administrator.
    """
    id_card_type_dal = IdCardTypeDAL(db)
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=404, detail="Tipo de documento de identidad no encontrado.")
    return id_card_type

@router.patch("/{id_card_type_id}", response_model=IdCardTypeResponse,
               dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def update_id_card_type( # Renombrado de update_id_card_type_admin
    id_card_type_id: int,
    id_card_type_data: IdCardTypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza la información de un tipo de documento de identidad. Requiere rol de System Administrator.
    """
    id_card_type_dal = IdCardTypeDAL(db)
    updated_type = await id_card_type_dal.update_id_card_type(id_card_type_id, id_card_type_data)
    if not updated_type:
        raise HTTPException(status_code=404, detail="Tipo de documento de identidad no encontrado.")
    return updated_type

@router.delete("/{id_card_type_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(has_role(SYSTEM_ADMINISTRATOR))])
async def delete_id_card_type( # Renombrado de delete_id_card_type_admin
    id_card_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un tipo de documento de identidad. Requiere rol de System Administrator.
    """
    id_card_type_dal = IdCardTypeDAL(db)
    success = await id_card_type_dal.delete_id_card_type(id_card_type_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de documento de identidad no encontrado.")
    return {} # Retornar un dict vacío para 204 No Content


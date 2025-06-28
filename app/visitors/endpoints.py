from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db 

from core.models import Visitor, IdCardType

# Importa los esquemas de visitantes
from app.visitors.schemas import VisitorCreate, VisitorUpdate, VisitorResponse
from app.visitors.dal import VisitorDAL
from app.id_card_types.dal import IdCardTypeDAL

router = APIRouter(tags=["Visitors (Base CRUD)"])

# --- Endpoints CRUD para la entidad Visitor ---

@router.post("/", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor_base(
    visitor_in: VisitorCreate,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    id_card_type_dal = IdCardTypeDAL(db) # Necesario para validar el id_card_type_id

    # Validar que el id_card_type_id exista
    id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_in.id_card_type_id)
    if not id_card_type:
        raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    # Validar unicidad del id_card_number si es requerido
    if visitor_in.id_card_number:
        existing_visitor = await visitor_dal.get_visitor_by_id_card_number(visitor_in.id_card_number)
        if existing_visitor:
            raise HTTPException(status_code=400, detail="Ya existe un visitante con este número de identificación.")
    
    new_visitor = await visitor_dal.create_visitor(visitor_in)
    return new_visitor

@router.get("/", response_model=List[VisitorResponse])
async def get_all_visitors_base(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    visitors = await visitor_dal.get_visitors(skip=skip, limit=limit)
    return visitors

@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor_by_id_base(
    visitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    visitor = await visitor_dal.get_visitor_by_id(visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    return visitor

@router.patch("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor_base(
    visitor_id: int,
    visitor_in: VisitorUpdate,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    if visitor_in.id_card_type_id: # Si se intenta actualizar el tipo de ID
        id_card_type_dal = IdCardTypeDAL(db)
        id_card_type = await id_card_type_dal.get_id_card_type_by_id(visitor_in.id_card_type_id)
        if not id_card_type:
            raise HTTPException(status_code=400, detail="Tipo de documento de identidad no válido.")

    updated_visitor = await visitor_dal.update_visitor(visitor_id, visitor_in)
    if not updated_visitor:
        raise HTTPException(status_code=404, detail="Visitante no encontrado o no se pudo actualizar.")
    return updated_visitor

@router.delete("/{visitor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visitor_base(
    visitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    visitor_dal = VisitorDAL(db)
    success = await visitor_dal.delete_visitor(visitor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Visitante no encontrado.")
    return {"message": "Visitante eliminado exitosamente."}
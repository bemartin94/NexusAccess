from fastapi import APIRouter, Depends, HTTPException, status # Añadido status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import AsyncSessionLocal

from app.visitors.schemas import VisitorCreate, VisitorResponse, VisitorUpdate
from app.visitors.dal import VisitorDAL

# --- Importar seguridad y el esquema User para obtener el usuario actual ---
from app.auth.security import get_current_user
from app.users.schemas import UserResponse # Asumo que tienes un UserResponse schema para el usuario autenticado

router = APIRouter(tags=["Visitors"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=VisitorResponse, operation_id="create_visitor")
async def create_visitor(
    visitor_in: VisitorCreate,
    db: AsyncSession = Depends(get_db),
    # --- Añadida la dependencia para requerir autenticación ---
    current_user: UserResponse = Depends(get_current_user)
):
    # Opcional: Puedes usar current_user.id o current_user.venue_id aquí
    # por ejemplo, para asegurar que solo se registren visitantes para la sede del usuario
    # if visitor_in.venue_id != current_user.venue_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para registrar visitantes en esta sede.")

    return await VisitorDAL(db).create_visitor(visitor_in)

@router.get("/{visitor_id}", response_model=VisitorResponse, operation_id="read_visitor")
async def read_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user) # También requiere autenticación
):
    visitor = await VisitorDAL(db).get_by_id(visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    # Opcional: verificar si el visitante pertenece a la sede del usuario
    # if visitor.venue_id != current_user.venue_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para ver este visitante.")
    return visitor

@router.put("/{visitor_id}", response_model=VisitorResponse, operation_id="update_visitor")
async def update_visitor(
    visitor_id: int,
    visitor_in: VisitorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user) # También requiere autenticación
):
    visitor = await VisitorDAL(db).get_by_id(visitor_id) # Obtener para verificar sede si es necesario
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    # if visitor.venue_id != current_user.venue_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para actualizar este visitante.")

    updated_visitor = await VisitorDAL(db).update_visitor(visitor_id, visitor_in)
    if not updated_visitor: # Esto puede ocurrir si el ID no existe o no hay cambios
        raise HTTPException(status_code=404, detail="Visitor not found or no changes made") # Mejorar mensaje
    return updated_visitor

@router.delete("/{visitor_id}", response_model=dict, operation_id="delete_visitor")
async def delete_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user) # También requiere autenticación
):
    dal = VisitorDAL(db)
    # Opcional: Obtener visitante para verificar sede antes de eliminar
    # visitor = await dal.get_by_id(visitor_id)
    # if not visitor or visitor.venue_id != current_user.venue_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para eliminar este visitante.")

    deleted = await dal.delete(visitor_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return {"message": "Visitor deleted successfully"}
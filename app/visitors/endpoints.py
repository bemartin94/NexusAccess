from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import AsyncSessionLocal
from app.visitors.schemas import VisitorCreate, VisitorResponse, VisitorUpdate
from app.visitors.dal import VisitorDAL

router = APIRouter(tags=["Visitors"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=VisitorResponse, operation_id="create_visitor")
async def create_visitor(
    visitor_in: VisitorCreate,
    db: AsyncSession = Depends(get_db)
):
    return await VisitorDAL(db).create_visitor(visitor_in)

@router.get("/{visitor_id}", response_model=VisitorResponse, operation_id="read_visitor")
async def read_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    visitor = await VisitorDAL(db).get_visitor_by_id(visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor

@router.put("/{visitor_id}", response_model=VisitorResponse, operation_id="update_visitor")
async def update_visitor(
    visitor_id: int,
    visitor_in: VisitorUpdate,
    db: AsyncSession = Depends(get_db)
):
    visitor = await VisitorDAL(db).update_visitor(visitor_id, visitor_in)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor

@router.delete("/{visitor_id}", response_model=dict, operation_id="delete_visitor")
async def delete_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await VisitorDAL(db).dele

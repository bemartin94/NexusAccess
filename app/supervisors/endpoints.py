from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.supervisors import schemas, dal
from core.database import AsyncSessionLocal

router = APIRouter(tags=["Supervisors"])

<<<<<<< Updated upstream
@router.get("/")
async def users():
    return {"ejemplo": "ejemplo"}
=======
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.SupervisorResponse)
async def create_supervisor(
    supervisor: schemas.SupervisorCreate,
    db: AsyncSession = Depends(get_db)
):
    return await dal.SupervisorDAL(db).create_supervisor(supervisor)

@router.get("/", response_model=list[schemas.SupervisorResponse])
async def list_supervisors(
    db: AsyncSession = Depends(get_db)
):
    return await dal.SupervisorDAL(db).list_supervisors()

@router.get("/{supervisor_id}", response_model=schemas.SupervisorResponse)
async def get_supervisor(
    supervisor_id: int,
    db: AsyncSession = Depends(get_db)
):
    supervisor = await dal.SupervisorDAL(db).get_supervisor_by_id(supervisor_id)
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return supervisor

@router.patch("/{supervisor_id}", response_model=schemas.SupervisorResponse)
async def update_supervisor(
    supervisor_id: int,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    updated = await dal.SupervisorDAL(db).update_supervisor(supervisor_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return updated

@router.delete("/{supervisor_id}")
async def delete_supervisor(
    supervisor_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await dal.SupervisorDAL(db).delete_supervisor(supervisor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return {"deleted": success}
>>>>>>> Stashed changes

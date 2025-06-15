from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from core.models import Supervisor
from app.supervisors.schemas import SupervisorCreate, SupervisorUpdate, SupervisorResponse
from fastapi import HTTPException, status

class SupervisorDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_supervisor(self, supervisor_in: SupervisorCreate) -> SupervisorResponse:
        try:
            supervisor_data = supervisor_in.model_dump()
            new_supervisor = Supervisor(**supervisor_data)
            self.db.add(new_supervisor)
            await self.db.commit()
            await self.db.refresh(new_supervisor) 

            return SupervisorResponse.model_validate(new_supervisor, from_attributes=True)
        
        except IntegrityError as e:
            await self.db.rollback()
            if "UNIQUE constraint failed" in str(e) and "supervisors.email" in str(e): 
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A supervisor with this email address already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during creation: {e}"
            )

    async def get_supervisor_by_id(self, supervisor_id: int) -> Optional[SupervisorResponse]:
        result = await self.db.execute(select(Supervisor).filter(Supervisor.id == supervisor_id))
        supervisor = result.scalars().first()
        if not supervisor:
            return None
        return SupervisorResponse.model_validate(supervisor, from_attributes=True)

    async def list_supervisors(self, skip: int = 0, limit: int = 100) -> List[SupervisorResponse]:
        result = await self.db.execute(select(Supervisor).offset(skip).limit(limit))
        supervisors = result.scalars().all()
        return [SupervisorResponse.model_validate(s, from_attributes=True) for s in supervisors]

    async def update_supervisor(self, supervisor_id: int, updates: SupervisorUpdate) -> Optional[SupervisorResponse]:
        result = await self.db.execute(select(Supervisor).filter(Supervisor.id == supervisor_id))
        supervisor = result.scalars().first()
        
        if not supervisor:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        
        if 'email' in update_data and update_data['email'] != supervisor.email:
            existing_supervisor_with_email = await self.db.execute(
                select(Supervisor).filter(Supervisor.email == update_data['email'])
            )
            if existing_supervisor_with_email.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A supervisor with this email address already exists."
                )

        for key, value in update_data.items():
            setattr(supervisor, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(supervisor)
        
            return SupervisorResponse.model_validate(supervisor, from_attributes=True)
            
        except IntegrityError as e:
            await self.db.rollback()
            if "UNIQUE constraint failed" in str(e) and "supervisors.email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A supervisor with this email address already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error during update: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during supervisor update: {e}"
            )

    # D - DELETE
    async def delete_supervisor(self, supervisor_id: int) -> bool:
        result = await self.db.execute(select(Supervisor).filter(Supervisor.id == supervisor_id))
        supervisor = result.scalars().first()
        if not supervisor:
            return False
        await self.db.delete(supervisor)
        await self.db.commit()
        return True

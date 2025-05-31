from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import Supervisor
from app.supervisors.schemas import SupervisorCreate, SupervisorResponse

class SupervisorDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_supervisor(self, supervisor_data: SupervisorCreate) -> SupervisorResponse:
        supervisor = Supervisor(**supervisor_data.model_dump())
        self.db.add(supervisor)
        await self.db.commit()
        await self.db.refresh(supervisor)
        return SupervisorResponse.model_validate(supervisor)

    async def get_supervisor_by_id(self, supervisor_id: int) -> SupervisorResponse | None:
        result = await self.db.execute(select(Supervisor).filter(Supervisor.id == supervisor_id))
        supervisor = result.scalars().first()
        if supervisor:
            return SupervisorResponse.model_validate(supervisor)
        return None

    async def update_supervisor(self, supervisor_id: int, updates: dict) -> SupervisorResponse | None:
        supervisor = await self.db.get(Supervisor, supervisor_id)
        if not supervisor:
            return None
        for key, value in updates.items():
            setattr(supervisor, key, value)
        await self.db.commit()
        await self.db.refresh(supervisor)
        return SupervisorResponse.model_validate(supervisor)

    async def delete_supervisor(self, supervisor_id: int) -> bool:
        supervisor = await self.db.get(Supervisor, supervisor_id)
        if not supervisor:
            return False
        await self.db.delete(supervisor)
        await self.db.commit()
        return True

    async def list_supervisors(self, skip: int = 0, limit: int = 100) -> list[SupervisorResponse]:
        result = await self.db.execute(select(Supervisor).offset(skip).limit(limit))
        supervisors = result.scalars().all()
        return [SupervisorResponse.model_validate(s) for s in supervisors]

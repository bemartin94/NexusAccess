from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import Access
from .schemas import AccessBase, AccessResponse, AccessTimeResponse

def __init__(self, db_session: AsyncSession):
    self.db = db_session

async def create_access(self, access_data: AccessBase) -> AccessResponse:
    access = Access(**access_data.model_dump(exclude_unset=True))
    self.db.add(access)
    await self.db.commit()
    await self.db.refresh(access)
    return await self._build_access_response(access)

async def get_access_by_id(self, access_id: int) -> AccessResponse | None:
    result = await self.db.execute(select(Access).filter(Access.id == access_id))
    access = result.scalars().first()
    if not access:
        return None
    return await self._build_access_response(access)

async def update_access(self, access_id: int, updates: dict) -> AccessResponse | None:
    access = await self.get_access_by_id(access_id)
    if not access:
        return None
    for key, value in updates.items():
        setattr(access, key, value)
    await self.db.commit()
    await self.db.refresh(access)
    return await self._build_access_response(access)

async def delete_access(self, access_id: int) -> bool:
    access = await self.db.get(Access, access_id)
    if not access:
        return False
    await self.db.delete(access)
    await self.db.commit()
    return True

async def list_accesses(self, skip: int = 0, limit: int = 100) -> list[AccessResponse]:
    result = await self.db.execute(select(Access).offset(skip).limit(limit))
    accesses = result.scalars().all()
    return [await self._build_access_response(a) for a in accesses]

async def _build_access_response(self, access: Access) -> AccessResponse:
    visitor_name = f"{access.visitor.name} {access.visitor.last_name}" if access.visitor else None
    venue_name = access.venue.name if access.venue else None
    supervisor_name = f"{access.supervisor.name} {access.supervisor.last_name}" if access.supervisor else None
    access_time = None
    if access.access_time:
        access_time = AccessTimeResponse.from_orm(access.access_time)

    return AccessResponse(
        id=access.id,
        venue_id=access.venue_id,
        id_card_type_id=access.id_card_type_id,
        visitor_id=access.visitor_id,
        id_supervisor=access.id_supervisor,
        access_reason=access.access_reason,
        department=access.department,
        is_recurrent=access.is_recurrent,
        status=access.status,
        access_time=access_time,
        visitor_name=visitor_name,
        venue_name=venue_name,
        supervisor_name=supervisor_name,
    )

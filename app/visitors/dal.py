from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.visitors import schemas
from core.models import Visitor

class VisitorDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[schemas.VisitorResponse]:
        result = await self.db.execute(select(Visitor).offset(skip).limit(limit))
        visitors = result.scalars().all()
        return [schemas.VisitorResponse.model_validate(v) for v in visitors]

    async def get_by_id(self, visitor_id: int) -> schemas.VisitorResponse | None:
        result = await self.db.execute(select(Visitor).filter(Visitor.id == visitor_id))
        visitor = result.scalar_one_or_none()
        if visitor:
            return schemas.VisitorResponse.model_validate(visitor)
        return None

    async def create_visitor(self, visitor_create: schemas.VisitorCreate) -> schemas.VisitorResponse:
        visitor_data = visitor_create.model_dump()
        visitor = Visitor(**visitor_data)
        self.db.add(visitor)
        await self.db.commit()
        await self.db.refresh(visitor)
        return schemas.VisitorResponse.model_validate(visitor)

    async def update_visitor(self, visitor_id: int, visitor_update: schemas.VisitorUpdate) -> schemas.VisitorResponse | None:
        result = await self.db.execute(select(Visitor).filter(Visitor.id == visitor_id))
        visitor = result.scalar_one_or_none()
        if not visitor:
            return None

        update_data = visitor_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(visitor, key, value)

        await self.db.commit()
        await self.db.refresh(visitor)
        return schemas.VisitorResponse.model_validate(visitor)

    async def delete(self, visitor_id: int) -> bool:
        result = await self.db.execute(select(Visitor).filter(Visitor.id == visitor_id))
        visitor = result.scalar_one_or_none()
        if not visitor:
            return False
        await self.db.delete(visitor)
        await self.db.commit()
        return True

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import IdCardType
from .schemas import IdCardTypeCreate, IdCardTypeResponse

class IdCardTypeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_id_card_type(self, id_card_type_in: IdCardTypeCreate) -> IdCardTypeResponse:
        id_card_type = IdCardType(name=id_card_type_in.name)
        self.db.add(id_card_type)
        await self.db.commit()
        await self.db.refresh(id_card_type)
        return IdCardTypeResponse.from_orm(id_card_type)

    async def get_id_card_type(self, id_card_type_id: int) -> IdCardTypeResponse | None:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        if id_card_type:
            return IdCardTypeResponse.from_orm(id_card_type)
        return None

    async def list_id_card_types(self, skip: int = 0, limit: int = 100) -> list[IdCardTypeResponse]:
        result = await self.db.execute(select(IdCardType).offset(skip).limit(limit))
        id_card_types = result.scalars().all()
        return [IdCardTypeResponse.from_orm(i) for i in id_card_types]

    async def update_id_card_type(self, id_card_type_id: int, updates: dict) -> IdCardTypeResponse | None:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        if not id_card_type:
            return None
        for key, value in updates.items():
            setattr(id_card_type, key, value)
        await self.db.commit()
        await self.db.refresh(id_card_type)
        return IdCardTypeResponse.from_orm(id_card_type)

    async def delete_id_card_type(self, id_card_type_id: int) -> bool:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        if not id_card_type:
            return False
        await self.db.delete(id_card_type)
        await self.db.commit()
        return True

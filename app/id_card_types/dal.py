# app/id_card_types/dal.py
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from typing import List, Optional

from core.models import IdCardType
from app.id_card_types.schemas import IdCardTypeCreate, IdCardTypeUpdate

class IdCardTypeDAL:
    def __init__(self, db: AsyncSession): 
        self.db = db

    async def get_id_card_type_by_id(self, id_card_type_id: int) -> Optional[IdCardType]:
        result = await self.db.execute(select(IdCardType).where(IdCardType.id == id_card_type_id)) 
        return result.scalars().first()

    async def get_id_card_type_by_name(self, name: str) -> Optional[IdCardType]:
        result = await self.db.execute(select(IdCardType).where(IdCardType.name == name)) 
        return result.scalars().first()

    async def get_id_card_types(self, skip: int = 0, limit: int = 100) -> List[IdCardType]:
        result = await self.db.execute(select(IdCardType).offset(skip).limit(limit)) 
        return result.scalars().all()

    async def create_id_card_type(self, id_card_type_data: IdCardTypeCreate) -> IdCardType:
        new_id_card_type = IdCardType(name=id_card_type_data.name)
        self.db.add(new_id_card_type)
        await self.db.commit() 
        await self.db.refresh(new_id_card_type) 
        return new_id_card_type

    async def update_id_card_type(self, id_card_type_id: int, id_card_type_data: IdCardTypeUpdate) -> Optional[IdCardType]:
        id_card_type_to_update = await self.get_id_card_type_by_id(id_card_type_id)
        if not id_card_type_to_update:
            return None
        
        update_data = id_card_type_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(id_card_type_to_update, key, value)
            
        await self.db.commit() 
        await self.db.refresh(id_card_type_to_update) 
        return id_card_type_to_update

    async def delete_id_card_type(self, id_card_type_id: int) -> bool:
        id_card_type_to_delete = await self.get_id_card_type_by_id(id_card_type_id)
        if id_card_type_to_delete:
            await self.db.delete(id_card_type_to_delete) 
            await self.db.commit() 
            return True
        return False
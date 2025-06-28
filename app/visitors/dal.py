# app/visitors/dal.py
from sqlalchemy.ext.asyncio import AsyncSession # Importar AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from typing import List, Optional

from core.models import Visitor, IdCardType, Venue
from app.visitors.schemas import VisitorCreate, VisitorUpdate

class VisitorDAL:
    def __init__(self, db: AsyncSession): # Cambiado a AsyncSession
        self.db = db

    async def get_visitor_by_id(self, visitor_id: int) -> Optional[Visitor]:
        result = await self.db.execute( # await añadido
            select(Visitor)
            .options(joinedload(Visitor.id_card_type), joinedload(Visitor.registration_venue))
            .where(Visitor.id == visitor_id)
        )
        return result.scalars().first()

    async def get_visitor_by_id_card_number(self, id_card_number: str) -> Optional[Visitor]:
        result = await self.db.execute( # await añadido
            select(Visitor)
            .options(joinedload(Visitor.id_card_type), joinedload(Visitor.registration_venue))
            .where(Visitor.id_card_number == id_card_number)
        )
        return result.scalars().first()

    async def get_visitors(self, skip: int = 0, limit: int = 100) -> List[Visitor]:
        result = await self.db.execute( # await añadido
            select(Visitor)
            .options(joinedload(Visitor.id_card_type), joinedload(Visitor.registration_venue))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_visitor(self, visitor_data: VisitorCreate) -> Visitor:
        new_visitor = Visitor(
            name=visitor_data.name,
            last_name=visitor_data.last_name,
            id_card_number=visitor_data.id_card_number,
            phone=visitor_data.phone,
            email=visitor_data.email,
            picture=visitor_data.picture,
            purpose_of_visit=getattr(visitor_data, 'purpose_of_visit', None),
            id_card_type_id=visitor_data.id_card_type_id,
            registration_venue_id=visitor_data.registration_venue_id
        )
        self.db.add(new_visitor)
        await self.db.commit() # await añadido
        await self.db.refresh(new_visitor) # await añadido
        return new_visitor

    async def update_visitor(self, visitor_id: int, visitor_data: VisitorUpdate) -> Optional[Visitor]:
        visitor_to_update = await self.get_visitor_by_id(visitor_id)
        if not visitor_to_update:
            return None
        
        update_data = visitor_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(visitor_to_update, key, value)
            
        await self.db.commit() # await añadido
        await self.db.refresh(visitor_to_update) # await añadido
        return visitor_to_update

    async def delete_visitor(self, visitor_id: int) -> bool:
        visitor_to_delete = await self.get_visitor_by_id(visitor_id)
        if visitor_to_delete:
            await self.db.delete(visitor_to_delete) # await añadido
            await self.db.commit() # await añadido
            return True
        return False
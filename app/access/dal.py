# app/access/dal.py
from sqlalchemy.ext.asyncio import AsyncSession # Importar AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime

from core.models import Access, Visitor, Venue, User, IdCardType
from app.access.schemas import AccessCreate, AccessUpdate

class AccessDAL:
    def __init__(self, db: AsyncSession): # Cambiado a AsyncSession
        self.db = db

    async def get_access_log_by_id(self, access_id: int) -> Optional[Access]:
        result = await self.db.execute( # await añadido
            select(Access)
            .options(
                joinedload(Access.visitor),
                joinedload(Access.venue),
                joinedload(Access.logged_by_user),
                joinedload(Access.id_card_type_at_access)
            )
            .where(Access.id == access_id)
        )
        return result.scalars().first()

    async def get_access_logs(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        venue_id: Optional[int] = None,
        visitor_id: Optional[int] = None,
        logged_by_user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Access]:
        query = select(Access).options(
            joinedload(Access.visitor),
            joinedload(Access.venue),
            joinedload(Access.logged_by_user),
            joinedload(Access.id_card_type_at_access)
        )

        if venue_id:
            query = query.where(Access.venue_id == venue_id)
        if visitor_id:
            query = query.where(Access.visitor_id == visitor_id)
        if logged_by_user_id:
            query = query.where(Access.logged_by_user_id == logged_by_user_id)
        if status:
            query = query.where(Access.status == status)

        result = await self.db.execute(query.offset(skip).limit(limit)) # await añadido
        return result.scalars().all()

    async def create_access_log(self, access_data: AccessCreate) -> Access:
        new_access = Access(
            venue_id=access_data.venue_id,
            visitor_id=access_data.visitor_id,
            id_card_type_id=access_data.id_card_type_id,
            id_card_number_at_access=access_data.id_card_number_at_access,
            logged_by_user_id=access_data.logged_by_user_id,
            access_reason=access_data.access_reason,
            department=access_data.department,
            is_recurrent=access_data.is_recurrent,
            status=access_data.status,
        )
        self.db.add(new_access)
        await self.db.commit() # await añadido
        await self.db.refresh(new_access) # await añadido
        return new_access

    async def update_access_log(self, access_id: int, access_data: AccessUpdate) -> Optional[Access]:
        access_to_update = await self.get_access_log_by_id(access_id)
        if not access_to_update:
            return None
        
        update_data = access_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(access_to_update, key, value)
            
        await self.db.commit() # await añadido
        await self.db.refresh(access_to_update) # await añadido
        return access_to_update

    async def mark_access_exit_time(self, access_id: int) -> Optional[Access]:
        access_to_update = await self.get_access_log_by_id(access_id)
        if not access_to_update:
            return None
        
        if access_to_update.exit_time is None:
            access_to_update.exit_time = datetime.now()
            access_to_update.status = "Cerrado"
            await self.db.commit() # await añadido
            await self.db.refresh(access_to_update) # await añadido
        return access_to_update

    async def delete_access_log(self, access_id: int) -> bool:
        access_to_delete = await self.get_access_log_by_id(access_id)
        if access_to_delete:
            await self.db.delete(access_to_delete) # await añadido
            await self.db.commit() # await añadido
            return True
        return False
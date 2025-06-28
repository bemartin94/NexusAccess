# app/access/dal.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload 
from typing import List, Optional
from datetime import datetime, date, timezone 

from core.models import Visitor, Access, IdCardType, Venue 
from app.visitors.schemas import VisitorCreate, VisitorUpdate 
from app.access.schemas import AccessCreate, AccessUpdate 

class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_access_log(self, access_data: AccessCreate, entry_time: datetime) -> Access:
        # Crea el objeto Access
        new_access = Access(
            visitor_id=access_data.visitor_id,
            venue_id=access_data.venue_id,
            id_card_type_id=access_data.id_card_type_id,
            id_card_number_at_access=access_data.id_card_number_at_access,
            logged_by_user_id=access_data.logged_by_user_id,
            entry_time=entry_time, 
            access_reason=access_data.access_reason,
            department=access_data.department,
            is_recurrent=access_data.is_recurrent,
            status=access_data.status
        )
        
        self.db_session.add(new_access)
        await self.db_session.commit()
        await self.db_session.refresh(new_access)

        # Cargar eagerly las relaciones 'visitor' y 'id_card_type_at_access'
        # Esto asegura que los datos estén disponibles después de que la sesión se pueda cerrar
        loaded_access = await self.db_session.execute(
            select(Access)
            .options(selectinload(Access.visitor), selectinload(Access.id_card_type_at_access)) # <--- ¡CAMBIO AQUÍ!
            .filter(Access.id == new_access.id)
        )
        return loaded_access.scalars().first()

    async def get_access_records(
        self,
        skip: int = 0,
        limit: int = 100,
        date_filter: Optional[date] = None,
        id_card_filter: Optional[str] = None,
        venue_id: Optional[int] = None
    ) -> List[Access]:
        query = select(Access).options(
            selectinload(Access.visitor),       
            selectinload(Access.id_card_type_at_access),  # <--- ¡CAMBIO AQUÍ!
            selectinload(Access.logged_by_user) 
        )

        if date_filter:
            # Filtrar por la fecha de entrada
            query = query.filter(Access.entry_time.cast(date) == date_filter)

        if id_card_filter:
            query = query.filter(Access.id_card_number_at_access.ilike(f"%{id_card_filter}%"))
        
        if venue_id:
            query = query.filter(Access.venue_id == venue_id)

        result = await self.db_session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_access_record_by_id(self, access_id: int) -> Optional[Access]:
        result = await self.db_session.execute(
            select(Access)
            .options(selectinload(Access.visitor), selectinload(Access.id_card_type_at_access), selectinload(Access.logged_by_user)) # <--- ¡CAMBIO AQUÍ!
            .filter(Access.id == access_id)
        )
        return result.scalars().first()

    async def update_access(self, access_id: int, access_update_data: AccessUpdate) -> Optional[Access]:
        existing_access = await self.get_access_record_by_id(access_id)
        if not existing_access:
            return None

        for field, value in access_update_data.model_dump(exclude_unset=True).items():
            setattr(existing_access, field, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(existing_access)
        
        updated_access = await self.db_session.execute(
            select(Access)
            .options(selectinload(Access.visitor), selectinload(Access.id_card_type_at_access), selectinload(Access.logged_by_user)) # <--- ¡CAMBIO AQUÍ!
            .filter(Access.id == access_id)
        )
        return updated_access.scalars().first()

    async def mark_access_exit_time(self, access_id: int) -> Optional[Access]:
        access_log = await self.get_access_record_by_id(access_id) 
        if not access_log:
            return None

        access_log.exit_time = datetime.now(timezone.utc) 
        access_log.status = "Finalizado"
        await self.db_session.commit()
        await self.db_session.refresh(access_log)
        
        return access_log

    async def delete_access(self, access_id: int) -> bool:
        access_record = await self.get_access_record_by_id(access_id)
        if not access_record:
            return False
        await self.db_session.delete(access_record)
        await self.db_session.commit()
        return True

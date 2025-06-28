# app/access/dal.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, cast # Importar and_ para combinar condiciones, cast para la conversión
from sqlalchemy.types import Date # Importar Date específicamente de sqlalchemy.types
from sqlalchemy.orm import selectinload 
from typing import List, Optional
from datetime import datetime, date, timezone, timedelta # Importar timedelta

# Importar TODOS los modelos que necesitas para las relaciones de carga eager
from core.models import Visitor, Access, IdCardType, Venue, User 
from app.visitors.schemas import VisitorCreate, VisitorUpdate 
from app.access.schemas import AccessCreate, AccessUpdate 

class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_access_log(self, access_data: AccessCreate, entry_time: datetime) -> Access:
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

        # Cargar eagerly TODAS las relaciones necesarias para las @property y computed fields
        loaded_access = await self.db_session.execute(
            select(Access)
            .options(
                selectinload(Access.visitor),               
                selectinload(Access.id_card_type_at_access), 
                selectinload(Access.logged_by_user),       
                selectinload(Access.venue)                 
            ) 
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
        # Cargar eagerly TODAS las relaciones necesarias para las @property y computed fields
        query = select(Access).options(
            selectinload(Access.visitor),       
            selectinload(Access.id_card_type_at_access),  
            selectinload(Access.logged_by_user),
            selectinload(Access.venue) 
        )

        if date_filter:
            # Obtener el inicio y fin del día para el filtro de fecha
            start_of_day = datetime.combine(date_filter, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(date_filter, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # Filtrar por rango de tiempo para asegurar que se incluyan todos los registros de ese día
            query = query.filter(
                and_(
                    Access.entry_time >= start_of_day,
                    Access.entry_time <= end_of_day
                )
            )

        if id_card_filter:
            query = query.filter(Access.id_card_number_at_access.ilike(f"%{id_card_filter}%"))
        
        if venue_id: 
            query = query.filter(Access.venue_id == venue_id)

        result = await self.db_session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_access_record_by_id(self, access_id: int) -> Optional[Access]:
        result = await self.db_session.execute(
            select(Access)
            .options(
                selectinload(Access.visitor), 
                selectinload(Access.id_card_type_at_access), 
                selectinload(Access.logged_by_user), 
                selectinload(Access.venue)
            ) 
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
        
        return await self.get_access_record_by_id(existing_access.id) 

    async def mark_access_exit_time(self, access_id: int) -> Optional[Access]:
        access_log = await self.get_access_record_by_id(access_id) 
        if not access_log:
            return None

        access_log.exit_time = datetime.now(timezone.utc) 
        access_log.status = "Finalizado"
        await self.db_session.commit()
        await self.db_session.refresh(access_log)
        
        return await self.get_access_record_by_id(access_log.id)

    async def delete_access(self, access_id: int) -> bool:
        access_record = await self.get_access_record_by_id(access_id)
        if not access_record:
            return False
        await self.db_session.delete(access_record)
        await self.db_session.commit()
        return True

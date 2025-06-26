from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, String # <--- Importar 'cast' y 'String'
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime

# Importaciones de modelos y esquemas
from core.models import Access, AccessTime, Visitor, IdCardType, Venue, User, Role
from app.access.schemas import AccessCreate, AccessUpdate, AccessResponse
from app.visitors.schemas import VisitorCreate


class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_access(self, access_data: AccessCreate, entry_datetime: datetime) -> AccessResponse:
        new_access = Access(
            venue_id=access_data.venue_id,
            visitor_id=access_data.visitor_id,
            id_card_type_id=access_data.id_card_type_id,
            supervisor_id=access_data.supervisor_id,
            access_reason=access_data.access_reason,
            department=access_data.department,
            is_recurrent=access_data.is_recurrent,
            status=access_data.status
        )
        self.db_session.add(new_access)
        await self.db_session.flush()

        new_access_time = AccessTime(
            access_date=entry_datetime,
            exit_date=None,
            access_id=new_access.id
        )
        self.db_session.add(new_access_time)
        await self.db_session.commit()
        await self.db_session.refresh(new_access)
        
        access_with_details = await self._get_access_with_full_details(new_access.id)
        return AccessResponse.model_validate(access_with_details)

    async def get_access_record_by_id(self, access_id: int) -> Optional[Access]:
        query = select(Access).options(
            selectinload(Access.visitor),
            selectinload(Access.id_card_type),
            selectinload(Access.venue),
            selectinload(Access.supervisor),
            selectinload(Access.access_time)
        ).where(Access.id == access_id)
        
        result = await self.db_session.execute(query)
        access = result.scalars().unique().first()
        
        return access

    async def get_access_records(
        self,
        date_filter: Optional[date] = None,
        id_card_filter: Optional[str] = None,
        venue_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AccessResponse]:
        """
        Obtiene una lista de registros de acceso con filtros y paginación.
        Incluye los detalles completos de visitante, sede, supervisor y tiempos de acceso.
        """
        query = (
            select(Access)
            .options(
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.access_time),
                selectinload(Access.id_card_type),
            )
        )

        if venue_id is not None:
            query = query.where(Access.venue_id == venue_id)

        if date_filter:
            query = query.join(Access.access_time).where(
                func.date(AccessTime.access_date) == date_filter
            )

        if id_card_filter:
            # --- CORRECCIÓN CRUCIAL AQUÍ ---
            # Convertir el INTEGER id_card a TEXTO para poder usar .ilike()
            query = query.join(Access.visitor).where(
                cast(Visitor.id_card, String).ilike(f"%{id_card_filter}%")
            )

        # Ordenar por fecha de acceso (descendente)
        query = query.order_by(AccessTime.access_date.desc()) 
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)

        result = await self.db_session.execute(query)
        accesses_db = result.scalars().unique().all()

        return [AccessResponse.model_validate(access) for access in accesses_db]

    async def update_access(self, access_id: int, access_update: AccessUpdate) -> Optional[AccessResponse]:
        access = await self.db_session.get(Access, access_id, options=[selectinload(Access.access_time)])
        if not access:
            return None

        for field, value in access_update.model_dump(exclude_unset=True).items():
            if field != "exit_date":
                setattr(access, field, value)
        
        if access_update.exit_date is not None:
            if access.access_time:
                access.access_time.exit_date = access_update.exit_date
            else:
                new_access_time = AccessTime(
                    access_id=access_id, 
                    access_date=datetime.now(),
                    exit_date=access_update.exit_date
                )
                self.db_session.add(new_access_time)
                access.access_time = new_access_time 

        await self.db_session.commit()
        await self.db_session.refresh(access)

        updated_access_with_details = await self._get_access_with_full_details(access.id)
        return AccessResponse.model_validate(updated_access_with_details)


    async def delete_access(self, access_id: int) -> None:
        access_to_delete = await self.db_session.get(Access, access_id)
        if not access_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acceso no encontrado")
        
        await self.db_session.delete(access_to_delete)
        await self.db_session.commit()

    async def _get_access_with_full_details(self, access_id: int) -> Optional[Access]:
        stmt = select(Access) \
            .filter(Access.id == access_id) \
            .options(
                selectinload(Access.visitor),
                selectinload(Access.id_card_type),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.access_time)
            )
            
        result = await self.db_session.execute(stmt)
        access_db = result.scalars().unique().first() 

        return access_db


from fastapi import HTTPException 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from core.models import Access, Visitor, Venue, Supervisor, IdCardType, AccessTime
from .schemas import AccessBase, AccessResponse, AccessTimeResponse

class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_access(self, access_data: AccessBase) -> AccessResponse:
        access = Access(**access_data.model_dump(exclude_unset=True))
        self.db.add(access)
        await self.db.commit()
        await self.db.refresh(access) 

        newly_created_access = await self.get_access_by_id(access.id)
        if not newly_created_access:
            raise HTTPException(status_code=500, detail="Error al recuperar el acceso recién creado.")
        
        return await self._build_access_response(newly_created_access)

    async def get_access_by_id(self, access_id: int) -> AccessResponse | None:
        result = await self.db.execute(
            select(Access)
            .filter(Access.id == access_id)
            .options(
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.id_card_type),
                selectinload(Access.access_time)  
            )
        )
        access = result.scalars().first()
        if not access:
            return None
        return await self._build_access_response(access)

    async def update_access(self, access_id: int, updates: dict) -> AccessResponse | None:
        result = await self.db.execute(
            select(Access)
            .filter(Access.id == access_id)
            .options(
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.id_card_type), 
                selectinload(Access.access_time)   
            )
        )
        access = result.scalars().first()

        if not access:
            return None

        for key, value in updates.items():
            setattr(access, key, value)

        await self.db.commit()
        await self.db.refresh(access) 

        updated_access_obj = await self.get_access_by_id(access.id)
        if not updated_access_obj:
            raise HTTPException(status_code=500, detail="Error al recuperar el acceso actualizado.")

        return await self._build_access_response(updated_access_obj)

    async def delete_access(self, access_id: int) -> bool:
        access = await self.db.get(Access, access_id)
        if not access:
            return False
        await self.db.delete(access)
        await self.db.commit()
        return True

    async def list_accesses(self, skip: int = 0, limit: int = 100) -> list[AccessResponse]:
        result = await self.db.execute(
            select(Access)
            .options(
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.id_card_type), 
                selectinload(Access.access_time)  
            )
            .offset(skip)
            .limit(limit)
        )
        accesses = result.scalars().all()
        return [await self._build_access_response(a) for a in accesses]

    async def _build_access_response(self, access: Access) -> AccessResponse:

        visitor_name = f"{access.visitor.name} {access.visitor.last_name}" if access.visitor else None

        venue_name = access.venue.name if access.venue else None
        
        supervisor_name = f"{access.supervisor.name} {access.supervisor.last_name}" if access.supervisor else None
        

        id_card_type_name = access.id_card_type.name if access.id_card_type else None

        access_time_response = None
        if access.access_time:
            access_time_response = AccessTimeResponse.model_validate(access.access_time) 
        
        return AccessResponse(
            id=access.id,
            venue_id=access.venue_id,
            id_card_type_id=access.id_card_type_id,
            visitor_id=access.visitor_id,
            supervisor_id=access.supervisor_id,
            access_reason=access.access_reason,
            department=access.department,
            is_recurrent=access.is_recurrent,
            status=access.status,
            access_time=access_time_response, 
            visitor_name=visitor_name,
            venue_name=venue_name,
            supervisor_name=supervisor_name,
            id_card_type_name=id_card_type_name 
        )
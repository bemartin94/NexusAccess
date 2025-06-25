from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime

# Importaciones de modelos y esquemas
from core.models import Access, AccessTime, Visitor, IdCardType, Venue, User, Role, user_roles
from app.access.schemas import AccessCreate, AccessUpdate, AccessResponse
from app.visitors.schemas import VisitorCreate


class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_access(self, access_data: AccessCreate, entry_datetime: datetime) -> AccessResponse:
        """
        Crea un nuevo registro de acceso y su tiempo de acceso asociado.
        """
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


    async def get_access_record_by_id(self, access_id: int):
        """
        Obtiene un registro de acceso por su ID, incluyendo todos los detalles relacionados.
        """
        query = select(Access).where(Access.id == access_id)
        result = await self.db_session.execute(query)
        access = result.scalar_one_or_none()
        
        if access:
            # Refresh para cargar explícitamente las relaciones
            await self.db_session.refresh(access, attribute_names=['visitor', 'id_card_type', 'venue', 'supervisor', 'access_time'])
            
            # Asegurarse de que access_time no es None para evitar errores
            if access.access_time is None:
                # Si es una relación de uno a uno y AccessTime no existe, es None.
                # Aquí podrías asignar un AccessTime 'vacío' o simplemente dejarlo como None.
                # Como tu AccessResponse maneja None, no necesitamos forzar una lista.
                pass 

            return access
        return None

    async def update_access(self, access_id: int, access_update: AccessUpdate):
        """
        Actualiza un registro de acceso existente.
        """
        access = await self.db_session.get(Access, access_id)
        if not access:
            return None

        for field, value in access_update.model_dump(exclude_unset=True).items():
            setattr(access, field, value)
        
        # Si se está actualizando la hora de salida, buscar el AccessTime y actualizarlo
        if access_update.exit_date is not None:
            # Acceder directamente a la relación access_time (singular)
            if access.access_time:
                access.access_time.exit_date = access_update.exit_date
            else:
                # Si no hay AccessTime asociado, crea uno nuevo para esta salida
                new_access_time = AccessTime(access_id=access_id, access_date=datetime.now(), exit_date=access_update.exit_date)
                self.db_session.add(new_access_time)
                # Establece la relación en el objeto Access para que SQLAlchemy la vea
                access.access_time = new_access_time 

        await self.db_session.commit()
        await self.db_session.refresh(access)
        
        updated_access_with_details = await self._get_access_with_full_details(access.id)
        return AccessResponse.model_validate(updated_access_with_details)


    async def delete_access(self, access_id: int):
        """
        Elimina un registro de acceso y sus tiempos asociados.
        Debido a cascade="all, delete-orphan", eliminar Access debería eliminar AccessTime automáticamente.
        """
        access_to_delete = await self.db_session.get(Access, access_id)
        if not access_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de acceso no encontrado")
        
        await self.db_session.delete(access_to_delete)
        await self.db_session.commit()


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
        Incluye los detalles completos de visitante, sede, supervisor y tiempos.
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
            query = query.join(Access.visitor).where(
                Visitor.id_card.ilike(f"%{id_card_filter}%")
            )

        query = query.order_by(AccessTime.access_date.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db_session.execute(query)
        accesses_db = result.unique().scalars().all()

        return [AccessResponse.model_validate(access) for access in accesses_db]

    async def _get_access_with_full_details(self, access_id: int):
        """
        Método auxiliar para cargar un registro de acceso con todas sus relaciones
        para el schema de respuesta.
        """
        # --- ¡CORRECCIÓN AQUÍ! Usar Access.access_time (singular) ---
        stmt = select(Access) \
            .filter(Access.id == access_id) \
            .join(Access.visitor) \
            .join(Access.id_card_type) \
            .join(Access.venue) \
            .join(Access.supervisor) \
            .outerjoin(Access.access_time) # <-- Cambiado de access_times a access_time
            
        result = await self.db_session.execute(stmt)
        access_db = result.unique().scalar_one_or_none() 

        if access_db:
            # access_time será None si no hay un registro relacionado. Las @property lo manejan.
            # No necesitamos forzar a que sea una lista ni asignar entry_date/exit_date aquí,
            # ya que las @property del modelo Access hacen ese trabajo de mapeo para Pydantic.
            pass

        return access_db
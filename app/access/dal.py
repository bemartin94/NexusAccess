from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from core.models import Access, AccessTime, IdCardType, Visitor, Venue, Supervisor # Importa todos los modelos relacionados
from app.access.schemas import AccessBase, AccessResponse # Asumiendo AccessBase para Create/Update y AccessResponse
from fastapi import HTTPException, status # Importa HTTPException y status

class AccessDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    # C - CREATE
    async def create_access(self, access_in: AccessBase) -> AccessResponse:
        try:
            access_data = access_in.model_dump(exclude_unset=True)
            new_access = Access(**access_data)
            self.db.add(new_access)
            await self.db.commit()
            
            # Refresca para obtener el ID generado por la base de datos
            await self.db.refresh(new_access)
            
            # Recargar el acceso con todas las relaciones para el AccessResponse
            # Esto es crucial para que las propiedades (@property) en el modelo Access
            # (como visitor_name) tengan los objetos relacionados disponibles para acceder a sus nombres.
            result = await self.db.execute(
                select(Access)
                .options(
                    selectinload(Access.access_time),
                    selectinload(Access.visitor),
                    selectinload(Access.venue),
                    selectinload(Access.supervisor),
                    selectinload(Access.id_card_type)
                )
                .filter(Access.id == new_access.id)
            )
            loaded_access = result.scalars().first()

            if not loaded_access:
                # Esto no debería pasar si el commit fue exitoso, pero es una buena verificación
                raise HTTPException(status_code=500, detail="Failed to retrieve created access with relationships after commit.")

            # Directamente serializa el objeto ORM cargado con from_attributes=True
            return AccessResponse.model_validate(loaded_access, from_attributes=True)
        
        except IntegrityError as e:
            await self.db.rollback()
            # Puedes añadir manejo de errores específico para UNIQUE constraints si Access tiene alguno
            # Por ejemplo, si access_reason combinado con venue_id fuera único.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during access creation: {e}"
            )

    # R - READ (Individual)
    async def get_access_by_id(self, access_id: int) -> Optional[AccessResponse]:
        result = await self.db.execute(
            select(Access)
            .options(
                selectinload(Access.access_time),
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.id_card_type)
            )
            .filter(Access.id == access_id)
        )
        access = result.scalars().first()
        if not access:
            return None
        # Directamente serializa el objeto ORM
        return AccessResponse.model_validate(access, from_attributes=True)

    # R - READ (Listado)
    async def list_accesses(self, skip: int = 0, limit: int = 100) -> List[AccessResponse]:
        result = await self.db.execute(
            select(Access)
            .options(
                selectinload(Access.access_time),
                selectinload(Access.visitor),
                selectinload(Access.venue),
                selectinload(Access.supervisor),
                selectinload(Access.id_card_type)
            )
            .offset(skip).limit(limit)
        )
        accesses = result.scalars().all()
        # Directamente serializa la lista de objetos ORM
        return [AccessResponse.model_validate(access, from_attributes=True) for access in accesses]

    # U - UPDATE
    async def update_access(self, access_id: int, access_update: AccessBase) -> Optional[AccessResponse]:
        result = await self.db.execute(select(Access).filter(Access.id == access_id))
        access = result.scalars().first()
        if not access:
            return None
        
        update_data = access_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(access, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(access) # Refresca el objeto ORM después de la actualización

            # Recargar el acceso con todas las relaciones después de la actualización
            # Esto es importante si la actualización podría afectar las relaciones o si el objeto
            # se cargó sin eager loading inicialmente.
            result = await self.db.execute(
                select(Access)
                .options(
                    selectinload(Access.access_time),
                    selectinload(Access.visitor),
                    selectinload(Access.venue),
                    selectinload(Access.supervisor),
                    selectinload(Access.id_card_type)
                )
                .filter(Access.id == access.id)
            )
            updated_access = result.scalars().first()
            if not updated_access:
                raise HTTPException(status_code=500, detail="Failed to retrieve updated access with relationships.")

            # Directamente serializa el objeto ORM actualizado
            return AccessResponse.model_validate(updated_access, from_attributes=True)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error during update: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during access update: {e}"
            )

    # D - DELETE
    async def delete_access(self, access_id: int) -> bool:
        result = await self.db.execute(select(Access).filter(Access.id == access_id))
        access = result.scalars().first()
        if not access:
            return False
        await self.db.delete(access)
        await self.db.commit()
        return True


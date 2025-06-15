from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # No es estrictamente necesario para IdCardType si no tiene relaciones complejas, pero buena práctica si se añadieran
from sqlalchemy.exc import IntegrityError # Importar para manejar errores de base de datos
from typing import Optional, List

from core.models import IdCardType
from app.id_card_types.schemas import IdCardTypeCreate, IdCardTypeUpdate, IdCardTypeResponse
from fastapi import HTTPException, status # Importar para lanzar excepciones HTTP

class IdCardTypeDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_id_card_type(self, id_card_type_in: IdCardTypeCreate) -> IdCardTypeResponse:
        try:
            # Usar .model_dump() para inicializar el objeto ORM de forma genérica
            id_card_type_data = id_card_type_in.model_dump()
            new_id_card_type = IdCardType(**id_card_type_data)
            
            self.db.add(new_id_card_type)
            await self.db.commit()
            await self.db.refresh(new_id_card_type) # Refrescar para obtener el ID generado

            # Usar model_validate con from_attributes=True para serializar la respuesta
            return IdCardTypeResponse.model_validate(new_id_card_type, from_attributes=True)
        except IntegrityError as e:
            await self.db.rollback() # Asegurarse de hacer rollback en caso de error
            # Manejar el error de unicidad específicamente para el campo 'name'
            if "UNIQUE constraint failed" in str(e) and "id_card_types.name" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An ID card type with this name already exists."
                )
            # Para otros IntegrityErrors no manejados específicamente, lanzar un 500
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}"
            )
        except Exception as e:
            await self.db.rollback() # Rollback para cualquier otra excepción
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during creation: {e}"
            )

    async def get_id_card_type(self, id_card_type_id: int) -> Optional[IdCardTypeResponse]:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        if not id_card_type:
            return None
        # Usar model_validate con from_attributes=True para serializar la respuesta
        return IdCardTypeResponse.model_validate(id_card_type, from_attributes=True)

    async def list_id_card_types(self, skip: int = 0, limit: int = 100) -> List[IdCardTypeResponse]:
        result = await self.db.execute(select(IdCardType).offset(skip).limit(limit))
        id_card_types = result.scalars().all()
        # Usar model_validate con from_attributes=True para serializar cada elemento de la lista
        return [IdCardTypeResponse.model_validate(i, from_attributes=True) for i in id_card_types]

    async def update_id_card_type(self, id_card_type_id: int, updates: IdCardTypeUpdate) -> Optional[IdCardTypeResponse]:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        
        if not id_card_type:
            return None
        
        # CAMBIO CRUCIAL: Usamos .model_dump(exclude_unset=True) para obtener solo los campos proporcionados para la actualización
        update_data = updates.model_dump(exclude_unset=True)
        
        # Manejo de unicidad si el campo 'name' es UNIQUE en la DB
        if 'name' in update_data and update_data['name'] != id_card_type.name:
            existing_type_with_name = await self.db.execute(
                select(IdCardType).filter(IdCardType.name == update_data['name'])
            )
            if existing_type_with_name.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An ID card type with this name already exists."
                )

        for key, value in update_data.items(): # Ahora update_data es un dict y .items() funciona
            setattr(id_card_type, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(id_card_type) # Refrescar para obtener el estado más reciente de la DB
            
            # Usar model_validate con from_attributes=True para serializar la respuesta
            return IdCardTypeResponse.model_validate(id_card_type, from_attributes=True)
            
        except IntegrityError as e:
            await self.db.rollback()
            if "UNIQUE constraint failed" in str(e) and "id_card_types.name" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An ID card type with this name already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error during update: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during ID Card Type update: {e}"
            )

    async def delete_id_card_type(self, id_card_type_id: int) -> bool:
        result = await self.db.execute(select(IdCardType).filter(IdCardType.id == id_card_type_id))
        id_card_type = result.scalars().first()
        if not id_card_type:
            return False
        await self.db.delete(id_card_type)
        await self.db.commit()
        return True

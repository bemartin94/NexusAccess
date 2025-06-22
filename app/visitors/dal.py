from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update 

from core.models import Visitor 
from app.visitors.schemas import VisitorCreate, VisitorUpdate

class VisitorDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_by_id(self, visitor_id: int):
        """
        Obtiene un visitante por su ID.
        """
        query = select(Visitor).where(Visitor.id == visitor_id)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def get_by_id_card(self, id_card: int):
        """
        Obtiene un visitante por su número de identificación (ID card).
        """
        query = select(Visitor).where(Visitor.id_card == id_card)
        result = await self.db_session.execute(query)
        return result.scalars().first()

    async def create_visitor(self, visitor_in: VisitorCreate):
        """
        Crea un nuevo visitante en la base de datos.
        """
        new_visitor = Visitor(**visitor_in.model_dump())
        self.db_session.add(new_visitor)
        await self.db_session.commit()
        await self.db_session.refresh(new_visitor)
        return new_visitor

    async def update_visitor(self, visitor_id: int, visitor_in: VisitorUpdate):
        """
        Actualiza los datos de un visitante existente.
        """
        # Filtra los campos None para no actualizar los que no se proporcionan
        update_data = visitor_in.model_dump(exclude_unset=True)

        if not update_data: # Si no hay datos para actualizar
            return None # O podrías devolver el visitante actual sin cambios

        query = update(Visitor).where(Visitor.id == visitor_id).values(**update_data)
        result = await self.db_session.execute(query)

        if result.rowcount == 0:
            return None # No se encontró el visitante para actualizar

        await self.db_session.commit()
        
        # Después de un update, si quieres devolver el objeto actualizado, necesitas consultarlo de nuevo
        updated_visitor = await self.get_by_id(visitor_id)
        return updated_visitor


    async def delete(self, visitor_id: int):
        """
        Elimina un visitante de la base de datos por su ID.
        """
        query = select(Visitor).where(Visitor.id == visitor_id)
        result = await self.db_session.execute(query)
        visitor = result.scalars().first()

        if not visitor:
            return False # No se encontró el visitante

        await self.db_session.delete(visitor)
        await self.db_session.commit()
        return True # Eliminado con éxito
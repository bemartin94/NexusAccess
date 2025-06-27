from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Aún necesitamos selectinload para el rol único y la sede
from typing import Optional, List

from core.models import User, Role # Importa Role si necesitas validar el ID del rol en DAL
from app.users.schemas import UserCreate, UserUpdate, UserResponse 
from fastapi import HTTPException 

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        # Crea una instancia del modelo User directamente desde el Pydantic model
        # Pydantic's model_dump() con exclude_unset=True manejará correctamente los campos opcionales
        # y el role_id directamente.
        user_data = user_create.model_dump(exclude_unset=True)
        
        # Elimina 'password' temporalmente para no pasarlo directamente si no lo has hasheado aquí
        # (se asume que ya fue hasheado en el endpoint).
        # Asegúrate de que el endpoint pasa 'password' ya hasheado.
        
        user = User(**user_data) # El role_id se asignará directamente aquí

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user) # Refresca para obtener el ID generado y las relaciones

        # Después de crear y refrescar, carga el usuario con sus relaciones
        # Ahora cargamos la relación 'role' (singular)
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO: selectinload(User.role)
            .filter(User.id == user.id) 
        )
        loaded_user = result.scalars().first()
        
        if not loaded_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve created user with relationships.")

        return UserResponse.model_validate(loaded_user) # from_attributes=True ya es el valor predeterminado en Pydantic v2+ si ConfigDict lo habilita

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO: selectinload(User.role)
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO: selectinload(User.role)
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Actualiza los atributos del usuario, incluyendo role_id si se proporciona
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user) # Refresca para que los cambios se reflejen, incluyendo el rol si cambió

        # Después de actualizar y refrescar, carga el usuario con sus relaciones actualizadas
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO: selectinload(User.role)
            .filter(User.id == user.id)
        )
        updated_user = result.scalars().first()
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated user with relationships.")

        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        # Carga eagerly las relaciones 'role' (singular) y 'venue'
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO: selectinload(User.role)
            .offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_email(self, email: str) -> Optional[User]: 
        # Esta función devuelve un objeto User de SQLAlchemy, no un esquema Pydantic.
        # No se necesita selectinload aquí a menos que el llamador necesite las relaciones inmediatamente.
        result = await self.db.execute(
            select(User)
            .filter(User.email == email)
        )
        return result.scalars().first()
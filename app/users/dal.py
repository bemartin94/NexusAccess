# app/users/dal.py
from sqlalchemy.ext.asyncio import AsyncSession # Importar AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from typing import List, Optional

from core.models import User, Role, Venue
from app.users.schemas import UserCreate, UserUpdate
from app.auth.security import get_password_hash

class UserDAL:
    def __init__(self, db: AsyncSession): # Cambiado a AsyncSession
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute( # await añadido
            select(User)
            .options(joinedload(User.role), joinedload(User.venue))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute( # await añadido
            select(User)
            .options(joinedload(User.role), joinedload(User.venue))
            .where(User.email == email)
        )
        return result.scalars().first()

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute( # await añadido
            select(User)
            .options(joinedload(User.role), joinedload(User.venue))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone=user_data.phone,
            password=hashed_password,
            role_id=user_data.role_id,
            venue_id=user_data.venue_id,
            is_active=user_data.is_active
        )
        self.db.add(new_user)
        await self.db.commit() # await añadido
        await self.db.refresh(new_user) # await añadido
        return new_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user_to_update = await self.get_user_by_id(user_id)
        if not user_to_update:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])

        for key, value in update_data.items():
            setattr(user_to_update, key, value)
        
        await self.db.commit() # await añadido
        await self.db.refresh(user_to_update) # await añadido
        return user_to_update
    
    async def delete_user(self, user_id: int) -> bool:
        user_to_delete = await self.get_user_by_id(user_id)
        if user_to_delete:
            await self.db.delete(user_to_delete) # await añadido
            await self.db.commit() # await añadido
            return True
        return False

    async def update_user_password(self, user: User, new_password: str) -> User:
        user.password = get_password_hash(new_password)
        await self.db.commit() # await añadido
        await self.db.refresh(user) # await añadido
        return user
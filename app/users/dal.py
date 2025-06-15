from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List

from core.models import User 
from app.users.schemas import UserCreate, UserUpdate, UserResponse 
from fastapi import HTTPException 

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(self, user_create: UserCreate) -> UserResponse:

        user = User(**user_create.model_dump(exclude_unset=True))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user) 

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.venue))
            .filter(User.id == user.id) 
        )
        loaded_user = result.scalars().first()
        
        if not loaded_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve created user with relationships.")

        return UserResponse.model_validate(loaded_user, from_attributes=True)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.venue))
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return None
        return UserResponse.model_validate(user, from_attributes=True)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.venue))
            .filter(User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)

        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.venue))
            .filter(User.id == user.id)
        )
        updated_user = result.scalars().first()
        if not updated_user:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated user with relationships.")

        return UserResponse.model_validate(updated_user, from_attributes=True)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        # Eager load the 'roles' and 'venue' relationships
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.venue))
            .offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [UserResponse.model_validate(user, from_attributes=True) for user in users]


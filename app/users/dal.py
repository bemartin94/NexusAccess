from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from core.models import User
from app.users.schemas import UserCreate, UserUpdate, UserResponse

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**user_create.model_dump(exclude_unset=True))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return None
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

# app/roles/dal.py
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from typing import List, Optional

from core.models import Role
from app.roles.schemas import RoleCreate

class RoleDAL:
    def __init__(self, db: AsyncSession): 
        self.db = db

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.id == role_id)) 
        return result.scalars().first()

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == role_name)) 
        return result.scalars().first()

    async def get_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        result = await self.db.execute(select(Role).offset(skip).limit(limit)) 
        return result.scalars().all()

    async def create_role(self, role_data: RoleCreate) -> Role:
        new_role = Role(name=role_data.name)
        self.db.add(new_role)
        await self.db.commit() 
        await self.db.refresh(new_role) 
        return new_role
 

    async def delete_role(self, role_id: int) -> bool:
        role_to_delete = await self.get_role_by_id(role_id)
        if role_to_delete:
            await self.db.delete(role_to_delete) 
            await self.db.commit() 
            return True
        return False
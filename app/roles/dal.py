from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import Role
from app.roles.schemas import RoleCreate, RoleResponse

class RoleDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_role(self, role_create: RoleCreate) -> RoleResponse:
        role = Role(name=role_create.name)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return RoleResponse.model_validate(role)

    async def get_role_by_id(self, role_id: int) -> RoleResponse | None:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalars().first()
        if role:
            return RoleResponse.model_validate(role)
        return None

    async def update_role(self, role_id: int, updates: dict) -> RoleResponse | None:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            return None
        for key, value in updates.items():
            setattr(role, key, value)
        await self.db.commit()
        await self.db.refresh(role)
        return RoleResponse.model_validate(role)

    async def delete_role(self, role_id: int) -> bool:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            return False
        await self.db.delete(role)
        await self.db.commit()
        return True

    async def list_roles(self, skip: int = 0, limit: int = 100) -> list[RoleResponse]:
        result = await self.db.execute(select(Role).offset(skip).limit(limit))
        roles = result.scalars().all()
        return [RoleResponse.model_validate(role) for role in roles]

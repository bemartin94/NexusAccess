from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Re-activar para eager loading de 'users'
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from core.models import Role, User # Asegúrate de importar Role y User
from app.roles.schemas import RoleCreate, RoleResponse # Asumo que tienes RoleCreate y RoleResponse
# from app.users.schemas import UserResponse # No es necesario si RoleResponse incluye List[int]
from fastapi import HTTPException, status

class RoleDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_role(self, role_create: RoleCreate) -> RoleResponse:
        try:
            role_data = role_create.model_dump()
            new_role = Role(**role_data)
            
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role) # Refrescar para obtener el ID

            # Volver a consultar el rol para asegurar que está en un estado que Pydantic pueda procesar
            # y que la relación 'users' esté eager-loaded para evitar MissingGreenlet
            result = await self.db.execute(
                select(Role)
                .options(selectinload(Role.users)) # Eager load la relación 'users'
                .filter(Role.id == new_role.id)
            )
            loaded_role = result.scalars().first()

            if not loaded_role:
                raise HTTPException(status_code=500, detail="Failed to retrieve created role.")

            return RoleResponse.model_validate(loaded_role, from_attributes=True)
        
        except IntegrityError as e:
            await self.db.rollback()
            if "UNIQUE constraint failed" in str(e) and "roles.name" in str(e): # Asumiendo que 'name' es unique
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A role with this name already exists."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during role creation: {e}"
            )

    async def get_role(self, role_id: int) -> Optional[RoleResponse]:
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.users)) # Eager load 'users' para get_role
            .filter(Role.id == role_id)
        )
        role = result.scalars().first()
        if not role:
            return None
        return RoleResponse.model_validate(role, from_attributes=True)

    async def list_roles(self, skip: int = 0, limit: int = 100) -> List[RoleResponse]:
        result = await self.db.execute(
            select(Role)
            .options(selectinload(Role.users)) # Eager load 'users' para list_roles
            .offset(skip).limit(limit)
        )
        roles = result.scalars().all()
        return [RoleResponse.model_validate(r, from_attributes=True) for r in roles]

    async def update_role(self, role_id: int, updates: RoleCreate) -> Optional[RoleResponse]: # Usando RoleCreate para updates como ejemplo
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        if 'name' in update_data and update_data['name'] != role.name:
            existing_role = await self.db.execute(
                select(Role).filter(Role.name == update_data['name'])
            )
            if existing_role.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A role with this name already exists."
                )

        for key, value in update_data.items():
            setattr(role, key, value)
        
        try:
            await self.db.commit()
            await self.db.refresh(role)
            
            # Recargar el rol con las relaciones después de la actualización
            result = await self.db.execute(
                select(Role)
                .options(selectinload(Role.users)) # Eager load 'users' para update_role
                .filter(Role.id == role.id)
            )
            updated_role = result.scalars().first()
            if not updated_role:
                raise HTTPException(status_code=500, detail="Failed to retrieve updated role.")

            return RoleResponse.model_validate(updated_role, from_attributes=True)
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error during role update: {e}"
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during role update: {e}"
            )

    async def delete_role(self, role_id: int) -> bool:
        result = await self.db.execute(select(Role).filter(Role.id == role_id))
        role = result.scalars().first()
        if not role:
            return False
        await self.db.delete(role)
        await self.db.commit()
        return True


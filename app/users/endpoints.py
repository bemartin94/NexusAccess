from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import schemas, dal
from core.database import AsyncSessionLocal
from typing import Optional, List # List is still needed if your schemas use it elsewhere
from core.models import User, Role, Venue
from sqlalchemy.future import select
from app.auth import security as auth_security

router = APIRouter(tags=["Users"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    # Optional: Add a dependency for authorization, e.g., only System Admins can create users
    # current_user: User = Depends(auth_security.has_role(auth_security.SYSTEM_ADMINISTRATOR))
):
    # Check if a user with the same email already exists
    existing_user = await dal.UserDAL(db).get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )

    # Hash the password
    hashed_password = auth_security.get_password_hash(user_in.password)
    
    # Create a new UserCreate instance with the hashed password
    # and adapt for the single role_id
    user_data = user_in.model_dump() # Get dictionary from Pydantic model
    user_data["password"] = hashed_password
    
    # Ensure the role_id is valid if provided
    if user_data.get("role_id") is not None:
        role_result = await db.execute(select(Role).filter(Role.id == user_data["role_id"]))
        if not role_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id provided."
            )

    # Pass the data to the DAL. The DAL will be responsible for creating the User model
    # with the correct role association.
    return await dal.UserDAL(db).create_user(schemas.UserCreate(**user_data))


@router.get("/", response_model=list[schemas.UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    # Add authorization if only certain roles can list users
    # current_user: User = Depends(auth_security.has_role(auth_security.SYSTEM_ADMINISTRATOR))
):
    return await dal.UserDAL(db).list_users()

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # Add authorization if only certain roles can view specific users
    # current_user: User = Depends(auth_security.get_current_active_user)
):
    user = await dal.UserDAL(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    # Add authorization if only certain roles can update users
    # current_user: User = Depends(auth_security.get_current_active_user)
):
    # If 'password' is provided in the update, hash it
    if user_update.password:
        user_update.password = auth_security.get_password_hash(user_update.password)

    # If 'role_id' is provided in the update, validate it
    if user_update.role_id is not None:
        role_result = await db.execute(select(Role).filter(Role.id == user_update.role_id))
        if not role_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id provided for update."
            )

    updated = await dal.UserDAL(db).update_user(user_id, user_update)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT) # Changed status code for successful deletion
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # Add authorization if only certain roles can delete users
    # current_user: User = Depends(auth_security.has_role(auth_security.SYSTEM_ADMINISTRATOR))
):
    deleted = await dal.UserDAL(db).delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    # For a 204 No Content response, typically no body is returned.
    # If you need a body, use 200 OK or 202 Accepted.
    return # No content returned for 204
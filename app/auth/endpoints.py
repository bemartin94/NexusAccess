
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.users import dal as users_dal
from app.users import schemas as users_schemas
from app.auth import schemas as auth_schemas
from app.auth import security as auth_security # Importa el módulo de seguridad

from core.database import get_db # Importa get_db de core.database
from core.config import settings # Importa settings de core.config


router = APIRouter(tags=["Authentication"]) 
@router.post("/register", response_model=users_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: users_schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await users_dal.UserDAL(db).get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    
    hashed_password = auth_security.get_password_hash(user_in.password)
    user_to_create = user_in.model_copy(update={"password": hashed_password})
    new_user = await users_dal.UserDAL(db).create_user(user_to_create)
    
    return new_user

@router.post("/token", response_model=auth_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await users_dal.UserDAL(db).get_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not auth_security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # Usando settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    access_token = auth_security.create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "venue_id": user.venue_id
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "venue_id": user.venue_id
    }

@router.get("/users/me", response_model=users_schemas.UserResponse)
async def read_users_me(current_user: users_schemas.UserResponse = Depends(auth_security.get_current_active_user)):
    return current_user
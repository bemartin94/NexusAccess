# app/auth/endpoints.py
from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr # Asegúrate de que EmailStr está aquí

# Importaciones desde tu proyecto
from core.database import get_db
from app.users.dal import UserDAL
from app.auth.security import verify_password, create_access_token, settings, get_current_active_user, get_password_hash
from app.users.schemas import UserResponse # Para el response_model de /me
from core.models import User # Para el tipo de 'current_user' en las dependencias

# --- Esquemas específicos para autenticación (Si los tienes en auth/schemas.py, impórtalos) ---
# Si estas clases ya están en app/auth/schemas.py, elimínalas de aquí y usa 'from app.auth.schemas import Token, UserUpdatePassword'
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_email: EmailStr
    user_role: Optional[str] = None
    venue_id: Optional[int] = None

class UserUpdatePassword(BaseModel):
    new_password: str = Field(..., min_length=8)

# --- Definición del Router (¡Sin prefijo aquí!) ---
router = APIRouter(tags=["Auth"]) # <--- CAMBIO: Eliminado prefix="/auth"

# --- Endpoint de Login ---
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    user = await user_dal.get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo.")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user=user,
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_email=user.email,
        user_role=user.role.name if user.role else None,
        venue_id=user.venue_id
    )

# --- Endpoint para obtener el perfil del usuario actual ---
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# --- Endpoint para que un usuario actualice su propia contraseña ---
@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_password(
    password_update: UserUpdatePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    user_dal = UserDAL(db)
    await user_dal.update_user_password(current_user, password_update.new_password)
    return {"message": "Contraseña actualizada exitosamente."}
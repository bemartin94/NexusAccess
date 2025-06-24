# app/auth/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.config import settings

from app.users.dal import UserDAL
from app.users.schemas import UserResponse # Asegúrate de que UserResponse tenga venue_id si lo usas directamente

# --- Configuración de Hashing de Contraseñas ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- Configuración y Funciones de JWT ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app/v1/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# --- Dependencias de Autenticación para FastAPI ---

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user_id: Optional[int] = payload.get("user_id")
    # --- ¡CORRECCIÓN CRÍTICA AQUÍ! Extraer venue_id del payload ---
    venue_id: Optional[int] = payload.get("venue_id")
    
    if email is None or user_id is None or venue_id is None: # Asegurar que venue_id no es None
        raise credentials_exception

    user_dal = UserDAL(db)
    # Aquí, podrías directamente construir UserResponse con los datos del payload
    # o asegurarte de que get_user_by_id devuelve un objeto con venue_id
    user = await user_dal.get_user_by_id(user_id) 

    if user is None:
        raise credentials_exception
    
    # --- Asegurarse de que UserResponse se construye con el venue_id del usuario ---
    # Si UserResponse no incluye venue_id, asegúrate de que tu modelo User lo tenga
    # y que UserResponse.model_validate(user) lo extraiga.
    # Si no, podrías pasar venue_id explícitamente:
    # return UserResponse(id=user.id, email=user.email, name=user.name, ..., venue_id=user.venue_id, is_active=user.is_active)
    
    # Asumiendo que UserResponse puede validar directamente el objeto 'user' completo
    # y que 'user' contiene 'venue_id', esto debería funcionar.
    return UserResponse.model_validate(user, from_attributes=True)


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependencia que verifica si el usuario autenticado está activo.
    """
    if not current_user.is_active: # Asume que UserResponse tiene un campo 'is_active'
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user

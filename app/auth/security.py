# app/auth/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel 
from core.models import User, Role 
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.database import get_db

# --- Settings ---
class Settings(BaseModel):
    SECRET_KEY: str = "efccbf380499240ee40eea5e7cb4d687" # ¡Cambia esto en producción!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()

# --- Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- JWT Token Handling ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app/v1/auth/token")

def create_access_token(user: User, expires_delta: Optional[timedelta] = None):
    to_encode = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.name if user.role else None, # Incluir el nombre del rol
        "venue_id": user.venue_id, # Incluir el ID de la sede
    }
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = {
            "user_id": int(user_id),
            "user_role_name": payload.get("role"),
            "user_venue_id": payload.get("venue_id")
        }
    except JWTError:
        raise credentials_exception
    return token_data # Retorna un dict con la data del token

async def get_current_active_user(
    token_data: dict = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Busca el usuario por ID
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.venue))
        .filter(User.id == token_data["user_id"])
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

# --- Dependencia para verificar roles ---
def has_role(required_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        # Si el usuario es un System Administrator, tiene acceso a todo,
        # sin importar los 'required_roles' específicos.
        if current_user.role and current_user.role.name == SYSTEM_ADMINISTRATOR[0]: # <--- ¡CLAVE: Usa el primer elemento de la lista!
            return current_user 

        # Si no es administrador o si el endpoint requiere roles específicos
        if not required_roles:
            # Si no se requieren roles específicos para este endpoint, y no es admin,
            # aún así se requiere que tenga un rol para ser válido.
            # Este caso es para endpoints que son 'públicos' pero requieren un usuario autenticado.
            if current_user.role:
                return current_user
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Se requiere autenticación y un rol válido."
                )

        # Si se requieren roles específicos, verificar si el rol del usuario está en esa lista.
        if current_user.role and current_user.role.name in required_roles:
            return current_user
        
        # Si no cumple con ninguno de los anteriores, denegar acceso.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. Required roles: {', '.join(required_roles)}. Your role: {current_user.role.name if current_user.role else 'None'}"
        )
    return role_checker

# Las constantes de roles ahora son listas de un solo elemento, lo cual es correcto para 'in required_roles'.
SYSTEM_ADMINISTRATOR = ["System Administrator"]
VENUE_SUPERVISOR = ["Venue Supervisor"]
RECEPTIONIST = ["Receptionist"]

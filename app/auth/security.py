# app/auth/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # ### CAMBIO AQUÍ: Importamos selectinload ###

from core.config import settings
from core.database import AsyncSessionLocal
from core.models import User, Role # ### CAMBIO AQUÍ: Importamos Role ###
from app.auth.schemas import TokenPayload # ### CAMBIO AQUÍ: Importamos TokenPayload ###

# Esquema de seguridad para OAuth2 con token de portador
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app/v1/auth/token")

# Contexto para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Hash de Contraseñas ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- Funciones de JWT ---
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Dependencia para la base de datos ---
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Dependencia para obtener el usuario actual a partir del token ---
async def get_current_active_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Aseguramos que el sub sea un string (email en nuestro caso, o ID si lo usas)
        # El sub aquí será el email del usuario.
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # ### CAMBIO AQUÍ: Validamos y extraemos los roles del payload ###
        token_data = TokenPayload(**payload)
        user_email = token_data.user_email
        user_id = token_data.user_id
        user_roles = token_data.user_roles # Esto ya vendrá del token
        venue_id = token_data.venue_id

    except JWTError:
        raise credentials_exception

    # ### CAMBIO AQUÍ: Cargamos el usuario incluyendo sus roles y sede ###
    # Usamos selectinload para cargar los roles y el venue en la misma consulta
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles), selectinload(User.venue))
        .filter(User.id == user_id, User.email == user_email)
    )
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    
    # ### CAMBIO AQUÍ: Verificamos que los roles cargados coincidan con los del token (opcional, pero buena práctica) ###
    # Esto asegura que si los roles del usuario cambian en la DB después de emitir el token,
    # el token se invalide para esas autorizaciones específicas.
    # if sorted(user.role_names) != sorted(user_roles):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User roles changed, please re-login.")
    
    return user

# --- Dependencia para verificar roles ---
def has_role(required_roles: List[str]):
    # Ensure current_user is obtained using the correct dependency function
    def role_checker(current_user: User = Depends(get_current_active_user)):
        # Si no se requieren roles, cualquier usuario autenticado pasa
        if not required_roles:
            return current_user
            
        # Comprueba si el usuario tiene AL MENOS UNO de los roles requeridos
        for role in required_roles:
            if role in current_user.role_names:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return role_checker

# Roles predefinidos para facilitar su uso
SYSTEM_ADMINISTRATOR = ["System Administrator"]
VENUE_SUPERVISOR = ["Venue Supervisor"]
GUEST_USER = ["Guest User"]
# Un usuario puede tener múltiples roles, por ejemplo:
# ADMIN_OR_SUPERVISOR = ["System Administrator", "Venue Supervisor"]

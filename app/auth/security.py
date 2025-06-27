from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Aún se usa para cargar User.role y User.venue

from core.config import settings
from core.database import AsyncSessionLocal
from core.models import User, Role # Asegúrate de que tus modelos ya estén actualizados
from app.auth.schemas import TokenPayload, UserResponse # Importamos UserResponse para tipo de current_user

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
# Modificado para aceptar User object y extraer su único rol
def create_access_token(
    user: User, expires_delta: Optional[timedelta] = None
) -> str:
    # Usamos el ID del usuario como 'sub' para identificar al usuario
    # y también incluimos el email, el rol único y el venue_id en el payload.
    to_encode = {
        "sub": str(user.id), # sub es el ID del usuario (debe ser string para JWT)
        "user_id": user.id,
        "user_email": user.email,
        "user_role": user.role_name, # CAMBIO AQUÍ: Ahora es un solo nombre de rol (puede ser None)
        "venue_id": user.venue_id, # Añadir el venue_id del usuario
    }
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode["exp"] = expire.timestamp() # El timestamp debe ser float

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Dependencia para la base de datos ---
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Dependencia para obtener el usuario actual a partir del token ---
# Se asegura de que el usuario devuelto sea un objeto User SQLAlchemy con las relaciones cargadas
async def get_current_active_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User: # Retorna un objeto User de SQLAlchemy
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Validar el payload con el esquema Pydantic TokenPayload
        token_data = TokenPayload(**payload) 
        
        user_id_from_token = token_data.user_id 
        user_email_from_token = token_data.user_email
        user_role_from_token = token_data.user_role # CAMBIO AQUÍ: Rol único del token
        venue_id_from_token = token_data.venue_id

        if user_id_from_token is None or user_email_from_token is None:
            raise credentials_exception
        
    except (JWTError, ValueError) as e:
        print(f"DEBUG: Error decoding or validating token payload: {e}")
        raise credentials_exception

    # Cargamos el usuario incluyendo su rol y sede
    # Esto es crucial para que current_user.role_name funcione
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.venue)) # CAMBIO AQUÍ: Cargamos User.role
        .filter(User.id == user_id_from_token, User.email == user_email_from_token)
    )
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    
    # Opcional pero recomendado: si el rol del token no coincide con la DB
    # Esto ayuda si el rol del usuario cambia en la DB después de emitir el token
    if user.role_name != user_role_from_token: # CAMBIO AQUÍ: Comparación de rol único
        print(f"DEBUG: User role from DB ({user.role_name}) does not match token role ({user_role_from_token}).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role changed, please re-login.")
    
    return user # Devuelve el objeto User de SQLAlchemy con las relaciones cargadas

# --- Dependencia para verificar roles ---
def has_role(required_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        # Si no se requieren roles, cualquier usuario autenticado pasa
        if not required_roles:
            return current_user
            
        # Comprueba si el usuario tiene AL MENOS UNO de los roles requeridos
        # Ahora current_user.role_name es un string (o None), no una lista
        if current_user.role_name in required_roles: # CAMBIO AQUÍ: Verificamos si el rol único está en la lista de requeridos
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return role_checker

# Roles predefinidos para facilitar su uso (Asegúrate que estos nombres coinciden con la DB)
SYSTEM_ADMINISTRATOR = ["System Administrator"]
VENUE_SUPERVISOR = ["Venue Supervisor"]
GUEST_USER = ["Guest User"]
# Un usuario ahora solo puede tener un rol, por lo que combinaciones como ADMIN_OR_SUPERVISOR
# ahora se usarían para verificar si el único rol del usuario es *uno de esos*.
ADMIN_OR_SUPERVISOR = ["System Administrator", "Venue Supervisor"]
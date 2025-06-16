from datetime import datetime, timedelta
from typing import Optional

import jwt # Importamos PyJWT
from jwt import PyJWTError # Clase de excepción para PyJWT
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings 
from core.database import AsyncSessionLocal # Necesario para la dependencia de DB
from core.models import User # Importamos el modelo User para obtener el usuario

# OAuth2PasswordBearer es una clase auxiliar de FastAPI para la seguridad basada en OAuth2
# Le decimos dónde esperar el token (en /app/v1/auth/token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/app/v1/auth/token")

# Contexto para el hash de contraseñas
# Usamos bcrypt como algoritmo por ser robusto y recomendado
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones para el Hashing de Contraseñas ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con una contraseña hasheada.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña en texto plano.
    """
    return pwd_context.hash(password)

# --- Funciones para JWT (JSON Web Tokens) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de acceso JWT.
    data: Diccionario con los datos a incluir en el payload del token (ej. {"sub": user_email}).
    expires_delta: Opcional, tiempo de vida del token. 
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Usamos el tiempo de expiración definido en core/config.py
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Añadimos el tiempo de expiración al payload
    to_encode.update({"exp": expire})
    
    # Codificamos el JWT usando la clave secreta y el algoritmo definidos en core/config.py
    # PyJWT.encode()
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un token de acceso JWT y extrae su payload.
    Devuelve el payload si es válido, None si el token es inválido o ha expirado.
    """
    try:
        # Decodificamos el token usando la clave secreta y el algoritmo
        # PyJWT.decode()
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except PyJWTError: # Captura la excepción específica de PyJWT
        # Captura cualquier error relacionado con JWT (ej. token inválido, expirado)
        return None

# --- Dependencia para proteger Endpoints ---

# Necesitamos una función para obtener la sesión de DB dentro de esta dependencia
async def get_db_for_security():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme), # FastAPI extrae el token del encabezado Authorization
    db: AsyncSession = Depends(get_db_for_security) # Obtiene una sesión de DB
) -> User: # Esta dependencia devolverá un objeto User ORM
    """
    Dependencia de FastAPI para obtener el usuario autenticado a partir de un JWT.
    Lanza HTTPException si el token es inválido, ha expirado o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar el token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Obtener el email del payload (el "sub" del token)
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Buscar el usuario en la base de datos
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    
    return user


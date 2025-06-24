from pydantic import BaseModel, ConfigDict, EmailStr # Usamos ConfigDict para Pydantic v2
from typing import Optional, List

# Importaciones de esquemas relacionados
from app.roles.schemas import RoleResponse
from app.venues.schemas import VenueResponse

class UserBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    # No incluimos 'password' aquí directamente para evitar pasarlo accidentalmente
    # en operaciones base donde no es necesario.
    phone: Optional[str] = None
    email: EmailStr
    venue_id: Optional[int] = None # ID de la sede a la que pertenece el usuario

    # Configuración del modelo para Pydantic (equivalente a Config en v1)
    model_config = ConfigDict(from_attributes=True, extra="forbid")

class UserCreate(UserBase):
    password: str # El password solo es necesario al crear un usuario

class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None # Permitir cambiar la contraseña
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    venue_id: Optional[int] = None
    is_active: Optional[bool] = None # Permite actualizar el estado de activo del usuario

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class UserResponse(UserBase):
    id: int
    is_active: bool = True # <-- ¡CRÍTICO! Añadido para que security.py funcione correctamente
    roles: List[RoleResponse] = [] # Lista de roles asociados al usuario
    venue: Optional[VenueResponse] = None # Información de la sede, opcional si no siempre se carga

    model_config = ConfigDict(from_attributes=True, extra="forbid")

# Esquema para el token JWT devuelto al cliente
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int # ID del usuario para el frontend
    venue_id: int # ID de la sede del usuario para el frontend

    model_config = ConfigDict(extra="forbid")

# Esquema para los datos decodificados del token JWT (uso interno)
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    venue_id: Optional[int] = None

    model_config = ConfigDict(extra="forbid")

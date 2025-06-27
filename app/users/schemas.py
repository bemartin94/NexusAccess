from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List

# No se necesitan importar RoleResponse ni VenueResponse directamente aquí
# si solo vas a exponer el nombre del rol o la sede en UserResponse.
# Si UserResponse va a anidar el objeto RoleResponse o VenueResponse completo,
# entonces sí serían necesarias. Para consistencia con auth/schemas, usaremos solo el nombre del rol.
# from app.roles.schemas import RoleResponse
# from app.venues.schemas import VenueResponse

class UserBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr
    venue_id: Optional[int] = None # ID de la sede a la que pertenece el usuario

    model_config = ConfigDict(from_attributes=True) # `extra="forbid"` puede ser problemático con ORM.

class UserCreate(UserBase):
    password: str # El password solo es necesario al crear un usuario
    role_id: Optional[int] = None # CAMBIO AQUÍ: Ahora se espera un único ID de rol

class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None # Permitir cambiar la contraseña
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    venue_id: Optional[int] = None
    is_active: Optional[bool] = None # Permite actualizar el estado de activo del usuario
    role_id: Optional[int] = None # CAMBIO AQUÍ: Permitir actualizar el ID del rol

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    is_active: bool = True # Crucial: Debe coincidir con el modelo SQLAlchemy User
    
    # CAMBIO AQUÍ: Ahora se expone el nombre del rol único del usuario
    # Pydantic mapeará automáticamente 'user.role.name' del modelo SQLAlchemy
    role_name: Optional[str] = Field(None, alias="role.name") 
    
    # Si quisieras la información completa de la sede, descomentarías esto
    # venue: Optional[VenueResponse] = None 
    # Y necesitarías importar `VenueResponse` arriba.
    # Para la sede, `UserResponse` en auth/schemas.py no tenía `venue`, así que mantendremos consistencia.

    model_config = ConfigDict(from_attributes=True)

# --- NOTA IMPORTANTE: Los esquemas Token y TokenData deben residir en app/auth/schemas.py ---
# No los dupliques aquí. Si se necesitan en otro lugar, impórtalos desde allí.
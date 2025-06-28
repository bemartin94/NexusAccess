# app/users/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = True # Añadido
    
    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8) # Contraseña obligatoria en la creación
    role_id: int
    venue_id: Optional[int] = None # Asignación de sede puede ser opcional al crear un usuario

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    role_id: Optional[int] = None # Para que el admin pueda cambiar roles
    venue_id: Optional[int] = None # Para que el admin pueda cambiar sedes
    password: Optional[str] = Field(None, min_length=8) # Permitir actualizar contraseña

class UserUpdateMe(BaseModel): # Para que el usuario actualice su propio perfil
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8) # Permitir actualizar contraseña

class UserResponse(UserBase):
    id: int
    role_id: int
    venue_id: Optional[int] = None
    role_name: Optional[str] = None # Propiedad del modelo User
    venue_name: Optional[str] = None # Para mostrar el nombre de la sede
    
    class Config:
        from_attributes = True
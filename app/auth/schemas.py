from pydantic import BaseModel, EmailStr, ConfigDict, Field 
from typing import Optional, List

class TokenPayload(BaseModel):
    sub: str # ID del usuario como string
    user_email: EmailStr # Email del usuario
    user_id: int
    venue_id: Optional[int] = None
    user_role: Optional[str] = None 
    exp: float # 'exp' debe ser float para aceptar timestamps con decimales

    model_config = ConfigDict(from_attributes=True, extra="ignore")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int # ID del usuario autenticado
    user_email: EmailStr # Email del usuario autenticado
    user_role: Optional[str] = None 
    venue_id: Optional[int] = None # ID de la sede del usuario (si aplica)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    role: Optional[str] = None 

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None
    role_id: Optional[int] = None 

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None
    
    # Si el `user.role` de SQLAlchemy es None, Pydantic lo mapeará a None automáticamente.
    role_name: Optional[str] = Field(None, alias="role.name") 

    model_config = ConfigDict(from_attributes=True) 

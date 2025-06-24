from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional,List

class TokenPayload(BaseModel):
    sub: str # Subject, generalmente el ID de usuario
    user_email: str
    user_id: int
    venue_id: Optional[int] = None # Puede ser nulo si el usuario no tiene una sede asignada
    user_roles: List[str] = [] # ### CAMBIO AQUÍ: Lista de strings para los roles ###
    exp: float # ### CAMBIO AQUÍ: 'exp' debe ser float para aceptar timestamps con decimales ###


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
    user_id: int  # Agrega el user_id
    venue_id: Optional[int] = None  # Agrega el venue_id (opcional, si un usuario puede no tener sede)
    user_id: int # ### CAMBIO AQUÍ: ID del usuario ###
    user_email: str # ### CAMBIO AQUÍ: Email del usuario ###
    user_roles: List[str] # ### CAMBIO AQUÍ: Roles del usuario autenticado ###

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class TokenData(BaseModel):
    email: Optional[str] = None
    # user_id: Optional[int] = None
    # roles: Optional[list[str]] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None # ### CAMBIO AQUÍ: venue_id puede ser opcional al crear un usuario ###
    role_ids: List[int] = [] # ### CAMBIO AQUÍ: Para asignar roles por ID al crear el usuario ###

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None
    roles: List[str] = [] # ### CAMBIO AQUÍ: Lista de nombres de roles ###

class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr, ConfigDict, computed_field # <-- computed_field es CRUCIAL
from typing import Optional, List

class TokenPayload(BaseModel):
    # 'sub' debería ser el ID del usuario para JWT si lo usas como identificador principal
    sub: str # ID del usuario como string
    user_email: EmailStr # Email del usuario
    user_id: int
    venue_id: Optional[int] = None
    user_roles: List[str] = [] # Lista de strings para los roles
    exp: float # 'exp' debe ser float para aceptar timestamps con decimales

    model_config = ConfigDict(from_attributes=True, extra="ignore") # Ignore extras para payload flexible


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
    user_roles: List[str] = [] # Roles del usuario autenticado
    venue_id: Optional[int] = None # ID de la sede del usuario (si aplica)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class TokenData(BaseModel):
    # Este esquema se usa generalmente para extraer solo datos del token
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    roles: Optional[List[str]] = None # Asegurarse de que el tipo es List[str] si se usa

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore" # Puede ignorar campos extra si el token tiene más de los que espera
    )

class UserCreate(BaseModel):
    email: EmailStr # Asegurarse que es EmailStr
    password: str
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None
    role_ids: List[int] = [] # Para asignar roles por ID al crear el usuario

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    venue_id: Optional[int] = None
    # ELIMINAR LA DECLARACIÓN DIRECTA DE ROLES AQUÍ (la línea de abajo)
    # roles: List[str] = [] 

    # Agregamos esta propiedad computada para que UserResponse pueda obtener los nombres de roles
    # del objeto User de SQLAlchemy cuando se usa `from_attributes=True`.
    @computed_field # <--- ¡ESTO ES LO QUE LE FALTABA A TU VERSIÓN!
    @property
    def roles(self) -> List[str]:
        # Asumiendo que `self` es una instancia de tu modelo SQLAlchemy `User`
        # y que tiene una relación `roles` que contiene objetos `Role`
        # con un atributo `name`.
        return [role.name for role in self.roles] if hasattr(self, 'roles') and self.roles else []

    model_config = ConfigDict(from_attributes=True, extra="forbid")
    # La clase `Config` que tenías al final debe ser `model_config = ConfigDict(...)` DENTRO de la clase.

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


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

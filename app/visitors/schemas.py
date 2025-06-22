from pydantic import BaseModel, EmailStr
from typing import Optional
# REMOVER: from datetime import date, time (ya no se necesitan aquí)

class VisitorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    id_card_type_id: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorCreate(VisitorBase):
    # Campos que son obligatorios al CREAR un visitante (persona)
    name: str
    last_name: str
    id_card: int
    email: EmailStr
    phone: str
    id_card_type_id: int
    # REMOVER: visit_date, entry_time, reason de aquí, ya que PERTENECEN A Access
    # visit_date: date
    # entry_time: time
    # reason: str

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorUpdate(VisitorBase):
    pass

class VisitorResponse(VisitorBase):
    id: int
    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
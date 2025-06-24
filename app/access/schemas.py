from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime, date, time

class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    visitor_id: Optional[int] = None
    supervisor_id: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str = "enabled"

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessCreate(AccessBase):
    pass

class VisitCreateRequest(BaseModel):
    name: str
    last_name: str
    id_card: str
    email: EmailStr
    phone: str
    id_card_type_id: int

    fecha: date
    hora_ing: time
    reason_visit: str
    sede: int
    supervisor_id: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorCreate(BaseModel):
    name: str
    last_name: str
    id_card: str
    email: EmailStr
    phone: str
    id_card_type_id: int
    supervisor_id: int
    venue_id: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorResponse(VisitorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    id_card_type_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessUpdate(BaseModel):
    exit_date: Optional[datetime] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessResponse(AccessBase):
    id: int
    entry_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None
    visitor_name: Optional[str] = None
    visitor_id_card: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    id_card_type_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )
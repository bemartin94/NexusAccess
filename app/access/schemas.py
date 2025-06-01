from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccessTimeBase(BaseModel):
    access_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None

class AccessTimeResponse(AccessTimeBase):
    id: int

    class Config:
        orm_mode = True

class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    visitor_id: Optional[int] = None
    id_supervisor: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str  # "enabled" o "denied"

class AccessResponse(AccessBase):
    id: int
    access_time: Optional[AccessTimeResponse] = None

    visitor_name: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None

    class Config:
        orm_mode = True

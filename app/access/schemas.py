from pydantic import BaseModel, ConfigDict 
from typing import Optional
from datetime import datetime

class AccessTimeBase(BaseModel):
    access_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None

class AccessTimeResponse(AccessTimeBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    visitor_id: Optional[int] = None
    supervisor_id: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str  # "enabled" o "denied"

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class AccessResponse(AccessBase):
    id: int
    access_time: Optional[AccessTimeResponse] = None

    visitor: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    id_card_type_name: Optional[str] = None 

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )
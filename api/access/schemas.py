from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AccessTimeBase(BaseModel):
    access_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None

class AccessTimeResponse(AccessTimeBase):
    id: int
    
    class Config:
        from_attributes = True

class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    id_card_id: int
    id_supervisor: int
    access_reason: Optional[str] = None
    is_recurrent: Optional[bool] = False

class AccessEnabledCreate(AccessBase):
    pass

class AccessDeniedCreate(AccessBase):
    department: Optional[str] = None

class AccessEnabledResponse(AccessBase):
    id: int
    access_time: Optional[AccessTimeResponse] = None
    visitor_name: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AccessDeniedResponse(AccessBase):
    id: int
    department: Optional[str] = None
    access_time: Optional[AccessTimeResponse] = None
    visitor_name: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class AccessLogResponse(BaseModel):
    id: int
    visitor_name: str
    id_card: str
    venue_name: str
    access_type: str  # "enabled" or "denied"
    access_date: Optional[datetime]
    exit_date: Optional[datetime]
    access_reason: Optional[str]
    supervisor_name: Optional[str]
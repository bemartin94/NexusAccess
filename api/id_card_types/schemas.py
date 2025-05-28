from pydantic import BaseModel
from typing import Optional, List

class IdCardTypeBase(BaseModel):
    name: str

class IdCardTypeCreate(IdCardTypeBase):
    pass

class IdCardTypeUpdate(BaseModel):
    name: Optional[str] = None

class IdCardTypeResponse(IdCardTypeBase):
    id: int
    enabled_visitors_count: int = 0
    denied_visitors_count: int = 0
    total_visitors_count: int = 0
    
    class Config:
        from_attributes = True

class IdCardTypeStats(BaseModel):
    id: int
    name: str
    enabled_visitors: int
    denied_visitors: int
    total_access_enabled: int
    total_access_denied: int
    last_access_date: Optional[str] = None
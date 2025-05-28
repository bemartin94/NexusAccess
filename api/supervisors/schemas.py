from pydantic import BaseModel, EmailStr
from typing import Optional, List

class SupervisorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr

class SupervisorCreate(SupervisorBase):
    pass

class SupervisorUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class SupervisorResponse(SupervisorBase):
    id: int
    venues_count: int = 0
    
    class Config:
        from_attributes = True

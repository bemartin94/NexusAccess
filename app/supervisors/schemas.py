from pydantic import BaseModel, EmailStr
from typing import Optional, List

class SupervisorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class SupervisorCreate(SupervisorBase):
    email: EmailStr 

class SupervisorResponse(SupervisorBase):
    id: int

    class Config:
        from_attributes = True

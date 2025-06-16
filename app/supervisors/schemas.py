from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List

class SupervisorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class SupervisorCreate(SupervisorBase):
    email: EmailStr 

class SupervisorUpdate(BaseModel): 
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None 

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class SupervisorResponse(SupervisorBase):
    id: int
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

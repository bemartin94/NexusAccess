from pydantic import BaseModel, EmailStr
from typing import Optional, List

class VisitorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None
    role_id: Optional[int] = None
    id_card_type_id: int

class EnabledVisitorCreate(VisitorBase):
    pass

class DeniedVisitorCreate(VisitorBase):
    pass

class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None
    role_id: Optional[int] = None

class VisitorResponse(VisitorBase):
    id: int
    id_card_type_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    venue_name: Optional[str] = None
    role_name: Optional[str] = None
    
    class Config:
        from_attributes = True

from pydantic import BaseModel, EmailStr
from typing import Optional

class VisitorBase(BaseModel):
    name: Optional[str] = None 
    last_name: Optional[str] = None
    id_card: Optional[int] = None 
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None
    id_card_type_id: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorCreate(VisitorBase):
    id_card: int 
    email: EmailStr 

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

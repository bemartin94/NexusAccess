from pydantic import BaseModel, EmailStr
from typing import Optional

class VisitorBase(BaseModel):
    name: Optional[str]
    last_name: Optional[str]
    id_card: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    picture: Optional[str]
    supervisor_id: Optional[int]
    venue_id: Optional[int]
    id_card_type_id: Optional[int]

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorCreate(VisitorBase):
    id_card: str
    email: EmailStr

class VisitorUpdate(VisitorBase):
    pass

class VisitorResponse(VisitorBase):
    id: int

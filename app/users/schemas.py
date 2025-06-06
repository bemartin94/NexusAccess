from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.roles.schemas import RoleResponse  
from app.venues.schemas import VenueResponse

class UserBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    email: EmailStr
    venue_id: Optional[int] = None

class UserCreate(UserBase):
    password: str  

class UserUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    venue_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    roles: List[RoleResponse] = []
    venue: Optional[VenueResponse] = None

    model_config = {
        "from_attributes": True
    }

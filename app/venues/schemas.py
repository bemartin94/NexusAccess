from pydantic import BaseModel
from typing import Optional

class VenueBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    supervisor_id: Optional[int] = None

class VenueCreate(VenueBase):
    pass

class VenueUpdate(VenueBase):
    pass

class VenueResponse(VenueBase):
    id: int

    class Config:
        from_attributes = True

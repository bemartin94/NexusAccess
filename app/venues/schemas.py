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

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
class VenueCreate(VenueBase):
    pass

class VenueUpdate(VenueBase):
       model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VenueResponse(VenueBase):
    id: int

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

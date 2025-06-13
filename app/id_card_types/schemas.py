from pydantic import BaseModel
from typing import Optional, List

class IdCardTypeBase(BaseModel):
    name: str

    model_config = {
    "from_attributes": True,
    "extra": "forbid"
}

class IdCardTypeCreate(IdCardTypeBase):
    name: str

    model_config = {
    "from_attributes": True,
    "extra": "forbid"
}

class IdCardTypeResponse(IdCardTypeBase):
    id: int

    class Config:
        
        model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


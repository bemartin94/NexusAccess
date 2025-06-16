from pydantic import BaseModel, ConfigDict
from typing import Optional, List 

class IdCardTypeBase(BaseModel):
    name: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class IdCardTypeCreate(IdCardTypeBase):
    pass 

class IdCardTypeUpdate(BaseModel):
    name: Optional[str] = None 

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class IdCardTypeResponse(IdCardTypeBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

from pydantic import BaseModel
from typing import Optional, List

class IdCardTypeBase(BaseModel):
    name: str

class IdCardTypeCreate(IdCardTypeBase):
    pass

class IdCardTypeResponse(IdCardTypeBase):
    id: int

    class Config:
        orm_mode = True

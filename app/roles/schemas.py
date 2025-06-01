from pydantic import BaseModel
from typing import Optional, List

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    users: Optional[List[int]] = None 

    class Config:
        orm_mode = True

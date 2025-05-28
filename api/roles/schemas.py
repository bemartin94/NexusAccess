from pydantic import BaseModel
from typing import List, Optional

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None

class RoleResponse(RoleBase):
    id: int
    users_count: int = 0
    
    class Config:
        from_attributes = True
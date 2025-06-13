from pydantic import BaseModel
from typing import Optional, List

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
        model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class RoleResponse(RoleBase):
    id: int
    users: Optional[List[int]] = None 


    model_config = {
    "from_attributes": True,
    "extra": "forbid"
}

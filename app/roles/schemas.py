from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    users: Optional[List[int]] = None 

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )


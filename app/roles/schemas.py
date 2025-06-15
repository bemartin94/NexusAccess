from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    # Hereda 'name' de RoleBase. No necesita model_config si es igual al padre.
    # Si quisieras validaciones adicionales solo para la creación, irían aquí.
    pass

class RoleResponse(RoleBase):
    id: int
    users: Optional[List[int]] = None 

    # model_config se define directamente en la clase
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )


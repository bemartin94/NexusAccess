from pydantic import BaseModel, ConfigDict
from typing import Optional, List # List no se usa aquí pero es una importación común

class IdCardTypeBase(BaseModel):
    name: str # 'name' es mandatorio en la base

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class IdCardTypeCreate(IdCardTypeBase):
    pass # Hereda 'name' como mandatorio de IdCardTypeBase

class IdCardTypeUpdate(BaseModel): # Heredamos de BaseModel directamente para hacer todos los campos opcionales
    name: Optional[str] = None # 'name' es opcional para la actualización

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class IdCardTypeResponse(IdCardTypeBase):
    id: int

    # Corrección: model_config se define directamente en la clase, no dentro de 'class Config' (eso era de Pydantic v1)
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

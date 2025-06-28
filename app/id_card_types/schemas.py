# app/id_card_types/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

# Esquema base para los atributos comunes de un tipo de tarjeta de identificación
class IdCardTypeBase(BaseModel):
    name: str = Field(..., example="DNI", description="Nombre del tipo de tarjeta de identificación (ej. DNI, Pasaporte)")

# Esquema para la creación de un nuevo tipo de tarjeta de identificación
class IdCardTypeCreate(IdCardTypeBase):
    pass

# Esquema para la actualización de un tipo de tarjeta de identificación existente
class IdCardTypeUpdate(IdCardTypeBase):
    name: Optional[str] = Field(None, example="Cédula", description="Nuevo nombre del tipo de tarjeta de identificación (opcional)")

# Esquema para la lectura/respuesta de un tipo de tarjeta de identificación
class IdCardType(IdCardTypeBase):
    id: int = Field(..., example=1, description="ID único del tipo de tarjeta de identificación")

class IdCardTypeResponse(IdCardTypeBase): # Renombrado de IdCardType a IdCardTypeResponse
    id: int = Field(..., example=1, description="ID único del tipo de tarjeta de identificación")

    class Config:
        from_attributes = True

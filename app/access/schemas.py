# app/access/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class AccessBase(BaseModel):
    venue_id: int
    visitor_id: int
    
    id_card_type_id: int # El tipo de documento usado en ESTE acceso
    id_card_number_at_access: str = Field(..., max_length=50) # El número de documento usado en ESTE acceso
    
    logged_by_user_id: int # ID del usuario (Recepcionista/Supervisor) que registró el acceso
    
    access_reason: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    is_recurrent: bool = False # Valor por defecto
    status: str = Field(..., max_length=50) # Ej. "Activo", "Cerrado", "Denegado"

    class Config:
        from_attributes = True

class AccessCreate(AccessBase):
    # entry_time no es necesario aquí, ya que tiene server_default en el modelo
    pass

class AccessUpdate(BaseModel):
    exit_time: Optional[datetime] = None # Para marcar la salida
    access_reason: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    is_recurrent: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50) # Para cambiar el estado del acceso manualmente

class AccessResponse(AccessBase):
    id: int
    entry_time: datetime
    exit_time: Optional[datetime] = None
    
    # Propiedades para facilitar la visualización en la respuesta
    visitor_full_name: Optional[str] = None
    venue_name: Optional[str] = None
    logged_by_user_email: Optional[EmailStr] = None
    id_card_type_name_at_access: Optional[str] = None

    class Config:
        from_attributes = True
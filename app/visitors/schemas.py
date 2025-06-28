# app/visitors/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, time, datetime

# --- Visitor Schemas ---
class VisitorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    id_card_number: str = Field(..., max_length=50, description="Número de identificación del visitante")
    id_card_type_id: int = Field(..., description="ID del tipo de documento de identidad")
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    picture: Optional[str] = None # URL o path de la imagen
    purpose_of_visit: Optional[str] = Field(None, max_length=255, description="Propósito principal de la visita del visitante")
    registration_venue_id: Optional[int] = Field(None, description="ID de la sede donde se registró inicialmente el visitante")

class VisitorCreate(VisitorBase):
    pass

class VisitorUpdate(BaseModel): # Solo los campos actualizables
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    id_card_number: Optional[str] = Field(None, max_length=50)
    id_card_type_id: Optional[int] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    purpose_of_visit: Optional[str] = Field(None, max_length=255)

class VisitorResponse(VisitorBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- VisitCreateRequest (para el endpoint register_full_visit) ---
# Este esquema DEBE coincidir con lo que el frontend envía y el backend espera.
# Basado en el último error 422:
class VisitCreateRequest(BaseModel):
    # Campos del visitante
    name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    id_card: str = Field(..., max_length=50, description="Número de identificación del visitante") # Ahora es 'id_card'
    id_card_type_id: int = Field(..., description="ID del tipo de documento de identidad")
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Campos de fecha/hora (obligatorios en el request)
    fecha: date = Field(..., description="Fecha de ingreso (YYYY-MM-DD)")
    hora_ing: time = Field(..., description="Hora de ingreso (HH:MM:SS)")
    
    # Campos de acceso
    reason_visit: str = Field(..., description="Motivo específico de esta visita") # Ahora es 'reason_visit'
    sede: int = Field(..., description="ID de la sede donde ocurre el acceso") # Ahora es 'sede'
    supervisor_id: int = Field(..., description="ID del supervisor (frontend lo envía prellenado)") # Ahora es 'supervisor_id'

    class Config:
        from_attributes = True

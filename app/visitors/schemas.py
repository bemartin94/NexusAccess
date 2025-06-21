from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time # Importar date y time para los nuevos campos

class VisitorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None
    id_card_type_id: Optional[int] = None
    # Añadidos campos para fecha y hora de la visita, y motivo
    # Asumo que estos son para el registro de la visita, no del "visitante" en sí.
    # Si estos campos son parte del "registro de visita" que relaciona un visitante con una visita en un momento,
    # deberías considerar un esquema de "VisitRecordCreate" separado.
    # Por ahora, los incluyo en VisitorBase, asumiendo que un "visitante" en tu contexto
    # es un registro de visita.
    visit_date: Optional[date] = None # Para el campo 'fecha'
    entry_time: Optional[time] = None # Para el campo 'hora_ing'
    reason: Optional[str] = None # Para el campo 'reason_visit'

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorCreate(VisitorBase):
    # Campos que son obligatorios al crear un visitante/registro de visita
    name: str # Hago estos obligatorios ya que son required en el frontend
    last_name: str
    id_card: int
    email: EmailStr
    phone: str
    supervisor_id: int
    venue_id: int
    id_card_type_id: int
    visit_date: date # Fecha de la visita es obligatoria
    entry_time: time # Hora de ingreso es obligatoria
    reason: str # Motivo de visita es obligatorio

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorUpdate(VisitorBase):
    pass

class VisitorResponse(VisitorBase):
    id: int
    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
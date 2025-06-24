# app/visitors/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time # Importar date y time para los campos de acceso

# Mantener VisitorBase, VisitorCreate, VisitorUpdate, VisitorResponse como ya los tienes
# ... (tu código VisitorBase, VisitorCreate, VisitorUpdate, VisitorResponse aquí) ...

class VisitorBase(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    id_card_type_id: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }

class VisitorCreate(VisitorBase):
    name: str
    last_name: str
    id_card: int
    email: EmailStr
    phone: str
    id_card_type_id: int
    supervisor_id: int 
    venue_id: int 

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

# --- NUEVO ESQUEMA: Para recibir la solicitud combinada del frontend ---
class VisitCreateRequest(BaseModel):
    # Datos del visitante (obligatorios para crear o buscar)
    name: str
    last_name: str
    id_card: int
    email: EmailStr
    phone: str
    id_card_type_id: int

    # Datos de la visita/acceso
    fecha: date # Corresponde a entry_date en AccessCreate
    hora_ing: time # Corresponde a entry_time en AccessCreate
    reason_visit: str # Corresponde a reason en AccessCreate
    sede: int # Corresponde a venue_id en AccessCreate
    supervisor_id: int # Corresponde a supervisor_id en AccessCreate

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


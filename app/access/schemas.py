# app/access/schemas.py

from pydantic import BaseModel, Field # Ya no necesitas computed_field aquí
from typing import Optional
from datetime import datetime

class AccessCreate(BaseModel):
    visitor_id: int
    venue_id: int
    id_card_type_id: int
    id_card_number_at_access: str
    logged_by_user_id: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str = "Activo"

class AccessUpdate(BaseModel):
    exit_time: Optional[datetime] = None
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = None
    status: Optional[str] = None

class AccessResponse(BaseModel):
    id: int
    visitor_id: int
    venue_id: int
    id_card_type_id: int
    id_card_number_at_access: str
    logged_by_user_id: int
    entry_time: datetime
    exit_time: Optional[datetime] = None
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 

    # ¡Deja que Pydantic lea estas propiedades directamente del modelo Access!
    # No declares @computed_field aquí.
    visitor_full_name: Optional[str] = None
    id_card_type_name_at_access: Optional[str] = None
    venue_name: Optional[str] = None
    logged_by_user_email: Optional[str] = None
    visitor_id_card: Optional[str] = None # Este es el único que tal vez quieras dejarlo como computed field si realmente quieres renombrarlo o derivarlo de otra forma, pero es directo de la columna.

    class Config: # Para Pydantic v1, o model_config para Pydantic v2
        from_attributes = True # Esto es lo que permite leer las @property del ORM
        # orm_mode = True # Si estás usando Pydantic v1
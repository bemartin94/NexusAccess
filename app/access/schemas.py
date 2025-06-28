# app/access/schemas.py

from pydantic import BaseModel, Field, EmailStr, computed_field
from typing import Optional
from datetime import datetime

# NO IMPORTAR AccessCreate, AccessUpdate de app.access.schemas aquí.
# Se definen en este mismo archivo.

class AccessCreate(BaseModel):
    visitor_id: int
    venue_id: int
    id_card_type_id: int
    id_card_number_at_access: str
    logged_by_user_id: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False # Aseguramos un valor por defecto si no es nulo
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
    is_recurrent: Optional[bool] = False # Aseguramos un valor por defecto si no es nulo
    status: str
    
    # IMPORTANTE: Estos campos serán Opcionales (o no aparecerán) si no están en tu modelo Access
    # Y si no se gestionan con server_default/onupdate.
    # Los hacemos Optional aquí para evitar un ResponseValidationError si no existen.
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None 

    # --- Computed Fields para el Frontend (basado en tus @property en models.py) ---
    @computed_field
    @property
    def visitor_full_name(self) -> Optional[str]:
        # Esto usará la @property de tu modelo Access.
        # Asegúrate de que self.visitor esté cargado eagerly en el DAL.
        return self.visitor.visitor_full_name if hasattr(self, 'visitor') and self.visitor else None

    @computed_field
    @property
    def venue_name(self) -> Optional[str]:
        # Esto usará la @property de tu modelo Access.
        # Asegúrate de que self.venue esté cargado eagerly en el DAL.
        return self.venue.venue_name if hasattr(self, 'venue') and self.venue else None

    @computed_field
    @property
    def logged_by_user_email(self) -> Optional[str]:
        # Esto usará la @property de tu modelo Access.
        # Asegúrate de que self.logged_by_user esté cargado eagerly en el DAL.
        return self.logged_by_user.logged_by_user_email if hasattr(self, 'logged_by_user') and self.logged_by_user else None

    @computed_field
    @property
    def id_card_type_name_at_access(self) -> Optional[str]:
        # Esto usará la @property de tu modelo Access.
        # Asegúrate de que self.id_card_type_at_access esté cargado eagerly en el DAL.
        return self.id_card_type_at_access.id_card_type_name_at_access if hasattr(self, 'id_card_type_at_access') and self.id_card_type_at_access else None

    @computed_field
    @property
    def visitor_id_card(self) -> str:
        # Esto se mapea directamente de la columna id_card_number_at_access
        return self.id_card_number_at_access

    class Config:
        from_attributes = True

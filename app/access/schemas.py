# app/access/schemas.py

from pydantic import BaseModel, ConfigDict, EmailStr, computed_field # <-- computed_field es esencial
from typing import Optional, List
from datetime import datetime, date, time

# --- Schemas para los modelos relacionados que serán cargados ---
# Estos son necesarios para que AccessResponse pueda "entender" y mapear las relaciones de SQLAlchemy
class AccessTimeSchema(BaseModel):
    id: int
    access_date: Optional[datetime] = None
    exit_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class VisitorSchema(BaseModel):
    id: int
    name: str
    last_name: Optional[str] = None # Añadido por si lo usas o necesitas en el futuro
    id_card: Optional[str] = None   # Asegúrate que el tipo coincida con tu modelo SQLAlchemy
    email: Optional[EmailStr] = None # Añadido
    phone: Optional[str] = None    # Añadido
    picture: Optional[str] = None # Añadido
    model_config = ConfigDict(from_attributes=True)

class VenueSchema(BaseModel):
    id: int
    name: str
    # Agrega otros campos de Venue si los necesitas en la respuesta
    model_config = ConfigDict(from_attributes=True)

class SupervisorSchema(BaseModel): # Asumiendo que Supervisor es un User o tiene campos similares
    id: int
    name: str
    last_name: Optional[str] = None
    # Agrega otros campos de Supervisor si los necesitas en la respuesta
    model_config = ConfigDict(from_attributes=True)

class IdCardTypeSchema(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

# --- FIN DE LOS NUEVOS ESQUEMAS PARA RELACIONES ---


class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    visitor_id: Optional[int] = None
    supervisor_id: int
    access_reason: Optional[str] = None
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str = "enabled"

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessCreate(AccessBase):
    # Puedes añadir campos específicos para la creación si difieren de AccessBase
    pass

class VisitCreateRequest(BaseModel):
    # Estos campos se usan para crear un visitante y un acceso
    name: str
    last_name: str
    id_card: str # El número de documento
    email: EmailStr
    phone: str
    id_card_type_id: int
    fecha: date # Fecha de la visita (para AccessTime)
    hora_ing: time # Hora de entrada (para AccessTime)
    reason_visit: str
    sede: int # Esto probablemente es el venue_id
    supervisor_id: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorCreate(BaseModel):
    name: str
    last_name: str
    id_card: str
    email: EmailStr
    phone: str
    id_card_type_id: int
    supervisor_id: int
    venue_id: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorResponse(VisitorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True, extra="forbid")

class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    id_card_type_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    venue_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessUpdate(BaseModel):
    exit_date: Optional[datetime] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

class AccessResponse(AccessBase):
    id: int
    
    # --- DECLARACIÓN DE LAS RELACIONES COMO CAMPOS PYDANTIC ---
    # Esto es crucial para que Pydantic sepa que estos objetos deben ser
    # mapeados desde el modelo SQLAlchemy si se usan computed_fields o si se acceden directamente.
    access_time: Optional[AccessTimeSchema] = None
    visitor: Optional[VisitorSchema] = None
    venue: Optional[VenueSchema] = None
    supervisor: Optional[SupervisorSchema] = None
    id_card_type: Optional[IdCardTypeSchema] = None

    # --- Los campos que se "computan" a partir de las relaciones ---
    # Ya NO SE DECLARAN directamente aquí, solo se definen como @computed_field
    # Pydantic v2 los inferirá de la implementación del computed_field.

    model_config = ConfigDict(
        from_attributes=True, # Permite mapear desde atributos del modelo SQLAlchemy
        extra="forbid"        # Evita campos no definidos
    )

    # --- Propiedades Computadas usando @computed_field ---
    # Estas funciones acceden a los objetos de las relaciones (self.access_time, self.visitor, etc.)
    # que deben haber sido cargadas por SQLAlchemy (ej. con selectinload en tu DAL).

    @computed_field
    @property # Opcional, pero ayuda con la tipificación y autocompletado en IDEs
    def entry_date(self) -> Optional[datetime]:
        """Extrae la fecha de entrada del objeto AccessTime relacionado."""
        return self.access_time.access_date if self.access_time else None

    @computed_field
    @property
    def exit_date(self) -> Optional[datetime]:
        """Extrae la fecha de salida del objeto AccessTime relacionado."""
        return self.access_time.exit_date if self.access_time else None
    
    @computed_field
    @property
    def visitor_id_card(self) -> Optional[str]:
        """Extrae el número de documento del visitante relacionado."""
        # Asegúrate de que 'id_card' en tu modelo Visitor es un String.
        # Si es un Integer en la DB, la conversión a str(..) es importante.
        return str(self.visitor.id_card) if self.visitor and self.visitor.id_card is not None else None

    @computed_field
    @property
    def visitor_name(self) -> Optional[str]:
        """Extrae el nombre completo del visitante relacionado."""
        # Puedes combinar nombre y apellido si lo deseas:
        # return f"{self.visitor.name} {self.visitor.last_name}" if self.visitor else None
        return self.visitor.name if self.visitor else None

    @computed_field
    @property
    def venue_name(self) -> Optional[str]:
        """Extrae el nombre de la sede relacionada."""
        return self.venue.name if self.venue else None

    @computed_field
    @property
    def supervisor_name(self) -> Optional[str]:
        """Extrae el nombre del supervisor relacionado."""
        return self.supervisor.name if self.supervisor else None

    @computed_field
    @property
    def id_card_type_name(self) -> Optional[str]:
        """Extrae el nombre del tipo de documento de identidad relacionado."""
        return self.id_card_type.name if self.id_card_type else None


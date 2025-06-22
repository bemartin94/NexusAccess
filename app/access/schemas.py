from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date, time # Importar date y time también

# El esquema para los tiempos de acceso.
# Considerando que el frontend envía fecha y hora por separado,
# y que el exit_date/time no se envía en la creación inicial.
class AccessTimeBase(BaseModel):
    # La fecha y hora de ingreso para la creación
    entry_date: date # Usar 'date'
    entry_time: time # Usar 'time'
    exit_date: Optional[date] = None
    exit_time: Optional[time] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

class AccessTimeResponse(AccessTimeBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

# El esquema base para el registro de acceso
class AccessBase(BaseModel):
    venue_id: int
    id_card_type_id: int
    visitor_id: Optional[int] = None # Este será el ID del visitante ya existente o recién creado
    supervisor_id: int
    reason: Optional[str] = None # Usé 'reason' para que coincida mejor con 'reason_visit' del frontend
    department: Optional[str] = None
    is_recurrent: Optional[bool] = False
    status: str = "enabled" # Valor por defecto 'enabled' si siempre inicia así

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

# Esquema para la creación de un registro de acceso desde el frontend
class AccessCreate(AccessBase):
    # Hereda los campos de AccessBase
    # Añadimos los campos de fecha y hora de entrada que vienen del frontend
    entry_date: date
    entry_time: time
    # El campo 'reason' (o access_reason) del frontend 'reason_visit' es obligatorio
    reason: str


# Esquema para actualizar un registro de acceso (ej. para registrar la salida)
class AccessUpdate(BaseModel):
    exit_date: Optional[date] = None
    exit_time: Optional[time] = None
    status: Optional[str] = None # Podrías cambiar el estado al salir, ej. "completed"

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

# Esquema para la respuesta de un registro de acceso
class AccessResponse(AccessBase):
    id: int
    # Para incluir los tiempos de acceso directamente, o como un objeto anidado
    # access_time: Optional[AccessTimeResponse] = None # Puedes mantenerlo si tienes una tabla AccessTimes separada
    # Si la fecha y hora de acceso son parte de la tabla principal de Access:
    entry_date: date
    entry_time: time
    exit_date: Optional[date] = None
    exit_time: Optional[time] = None


    # Campos adicionales para la respuesta que vienen de JOINs o relaciones
    visitor_name: Optional[str] = None
    venue_name: Optional[str] = None
    supervisor_name: Optional[str] = None
    id_card_type_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )
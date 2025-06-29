from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para valores por defecto de tiempo
from core.database import Base 
from typing import Optional, List

# --- Modelos del Sistema ---

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class IdCardType(Base):
    __tablename__ = "id_card_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  

    visitors = relationship("Visitor", back_populates="id_card_type") # Relación para visitantes
    accesses = relationship("Access", back_populates="id_card_type_at_access") # Relación para Access 

class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # Name debería ser obligatorio
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    
    main_supervisor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    
    users = relationship("User", back_populates="venue", foreign_keys="[User.venue_id]")
    main_supervisor_user = relationship("User", foreign_keys=[main_supervisor_user_id]) 

    visitors_registered = relationship("Visitor", back_populates="registration_venue") # Visitantes registrados en esta sede
    access_logs = relationship("Access", back_populates="venue") # Registros de acceso en esta sede

# --- Modelo de Usuarios Internos (Personal) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # El nombre debería ser obligatorio
    last_name = Column(String, nullable=False) # El apellido debería ser obligatorio
    password = Column(String, nullable=False) # La contraseña debería ser obligatoria para usuarios logeables
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False) # El email debería ser obligatorio y único
    is_active = Column(Boolean, default=True) # Un campo para activar/desactivar usuarios

    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True) # Sede a la que pertenece el usuario
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False) # Rol del usuario, debe ser obligatorio
    
    role = relationship("Role", back_populates="users")

    venue = relationship("Venue", back_populates="users", foreign_keys="[User.venue_id]") 
    
    venues_supervised = relationship("Venue", back_populates="main_supervisor_user", foreign_keys="[Venue.main_supervisor_user_id]")
    
    access_logs_logged = relationship("Access", back_populates="logged_by_user") 

    @property
    def role_name(self) -> Optional[str]:
        return self.role.name if self.role else None

# --- Modelo de Visitantes Externos ---
class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # Nombre del visitante
    last_name = Column(String, nullable=False) # Apellido del visitante
    
    id_card_number = Column(String, unique=True, index=True, nullable=True) # Número de identificación (DNI, Pasaporte, etc.)
    
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True) # El email puede o no ser único si no es obligatorio
    picture = Column(String, nullable=True) # URL o path de la imagen

    registration_venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    registration_venue = relationship("Venue", back_populates="visitors_registered")
    
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"), nullable=True)
    id_card_type = relationship("IdCardType", back_populates="visitors")
    
    access_logs = relationship("Access", back_populates="visitor") # Registros de acceso de este visitante


# --- Modelo de Registros de Acceso ---
class Access(Base):
    __tablename__ = "access_logs" # Renombrado para mayor claridad

    id = Column(Integer, primary_key=True, index=True)
    
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False) # No debería ser nulo si cada acceso es de un visitante
    
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"), nullable=False) # El tipo de documento usado en ESTE acceso
    id_card_number_at_access = Column(String, nullable=False) # El número de documento usado en ESTE acceso
    
    logged_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Usuario (Recepcionista/Supervisor) que registró el acceso

    entry_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)

    access_reason = Column(String, nullable=True) # Motivo específico de este acceso
    department = Column(String, nullable=True) # Departamento visitado
    is_recurrent = Column(Boolean, default=False) # Si es un visitante recurrente (ej. contratista diario)
    status = Column(String, nullable=False) # Ej. "Activo", "Cerrado", "Denegado"

    venue = relationship("Venue", back_populates="access_logs")
    visitor = relationship("Visitor", back_populates="access_logs")
    logged_by_user = relationship("User", back_populates="access_logs_logged") # El usuario interno que hizo el registro
    id_card_type_at_access = relationship("IdCardType", foreign_keys=[id_card_type_id]) # Relación al tipo de ID usado en ESTE acceso

    # Propiedades para facilitar el acceso a nombres relacionados
    @property
    def visitor_full_name(self) -> Optional[str]:
        return f"{self.visitor.name} {self.visitor.last_name}" if self.visitor else None

    @property
    def venue_name(self) -> Optional[str]:
        return self.venue.name if self.venue else None

    @property
    def logged_by_user_email(self) -> Optional[str]:
        return self.logged_by_user.email if self.logged_by_user else None

    @property
    def id_card_type_name_at_access(self) -> Optional[str]:
        return self.id_card_type_at_access.name if self.id_card_type_at_access else None
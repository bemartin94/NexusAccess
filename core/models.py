from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base
from typing import Optional
from datetime import datetime

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    venue = relationship("Venue", back_populates="users")

class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))

    users = relationship("User", back_populates="venue")
    supervisor = relationship("Supervisor", back_populates="venues")
    visitors = relationship("Visitor", back_populates="venue")
    


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    users = relationship("User", secondary=user_roles, back_populates="roles")


class Supervisor(Base):
    __tablename__ = "supervisors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)

    venues = relationship("Venue", back_populates="supervisor")
    visitors = relationship("Visitor", back_populates="supervisor")

class IdCardType(Base):
    __tablename__ = "id_card_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  

    visitors = relationship("Visitor", back_populates="id_card_type")

class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    id_card = Column(Integer, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    picture = Column(String, nullable=True)

    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))

    id_card_type = relationship("IdCardType", back_populates="visitors")
    supervisor = relationship("Supervisor", back_populates="visitors")
    venue = relationship("Venue", back_populates="visitors")


class AccessTime(Base):
    __tablename__ = "access_times"
    id = Column(Integer, primary_key=True, index=True)
    access_date = Column(DateTime, nullable=True) # Fecha y hora de acceso
    exit_date = Column(DateTime, nullable=True)   # Fecha y hora de salida

    access_id = Column(Integer, ForeignKey("accesses.id"))
    access = relationship("Access", back_populates="access_time")


class Access(Base):
    __tablename__ = "accesses"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=True)
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))
    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))

    access_reason = Column(String, nullable=True)
    department = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)
    status = Column(String, nullable=False) # ej. "enabled", "completed", "cancelled"

    # Relación uno a uno con AccessTime
    # cascade="all, delete-orphan" asegura que si eliminas un Access,
    # su AccessTime asociado también se elimina automáticamente.
    access_time = relationship("AccessTime", uselist=False, back_populates="access", cascade="all, delete-orphan")
    # Relaciones muchos a uno con otros modelos
    id_card_type = relationship("IdCardType")
    visitor = relationship("Visitor")
    venue = relationship("Venue")
    supervisor = relationship("Supervisor")

    # --- PROPIEDADES CALCULADAS (@property) ---
    # Estas propiedades permiten acceder a datos de relaciones o combinar campos
    # directamente desde el objeto Access, y son recogidas por Pydantic con from_attributes=True.

    @property
    def entry_date(self) -> Optional[datetime]:
        """Devuelve la fecha y hora de entrada del AccessTime asociado."""
        return self.access_time.access_date if self.access_time else None

    @property
    def exit_date(self) -> Optional[datetime]:
        """Devuelve la fecha y hora de salida del AccessTime asociado."""
        return self.access_time.exit_date if self.access_time else None

    @property
    def visitor_name(self) -> Optional[str]:
        """Devuelve el nombre del visitante asociado."""
        return self.visitor.name if self.visitor else None

    @property
    def visitor_id_card(self) -> Optional[str]:
        """Devuelve el número de documento del visitante asociado."""
        return self.visitor.id_card if self.visitor else None

    @property
    def venue_name(self) -> Optional[str]:
        """Devuelve el nombre del local asociado."""
        return self.venue.name if self.venue else None

    @property
    def supervisor_name(self) -> Optional[str]:
        """Devuelve el nombre del supervisor asociado."""
        # Ajusta esto si tu modelo Supervisor tiene first_name/last_name
        return self.supervisor.name if self.supervisor else None

    @property
    def id_card_type_name(self) -> Optional[str]:
        """Devuelve el nombre del tipo de tarjeta de identificación asociado."""
        return self.id_card_type.name if self.id_card_type else None
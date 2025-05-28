from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Time, Date
from sqlalchemy.orm import relationship, Table
from .database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id"))
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

class IdCardType(Base):
    __tablename__ = "id_card_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  

    enabled_visitors = relationship("EnabledVisitor", back_populates="id_card_type")
    denied_visitors = relationship("DeniedVisitor", back_populates="id_card_type")

class EnabledVisitor(Base):
    __tablename__ = "enabled_visitor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    id_card = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    picture = Column(String, nullable=True)

    supervisor_id = Column(Integer, ForeignKey("supervisor.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))

    id_card_type = relationship("IdCardType", back_populates="enabled_visitors")



"""pensamos como alternativa eliminar las clases deniedvisitor y accessdenied,
 que la clase se llame simplemente Visitor
y agregar un campo en la clase Visitor que sea is_enabled. Lo mismo para access"""
class DeniedVisitor(Base):
    __tablename__ = "denied_visitor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    id_card = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    picture = Column(String, nullable=True)

    supervisor_id = Column(Integer, ForeignKey("supervisor.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))

    id_card_type = relationship("IdCardType", back_populates="denied_visitors")

class AccessTime(Base):
    __tablename__ = "access_times"
    id = Column(Integer, primary_key=True, index=True)
    access_date = Column(DateTime, nullable=True)
    exit_date = Column(DateTime, nullable=True)

    access_enabled_id = Column(Integer, ForeignKey("access_enabled.id"))
    access_enabled = relationship("AccessEnabled", back_populates="access_time")


class AccessEnabled(Base):
    __tablename__ = "access_enabled"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))
    id_card_id = Column(Integer, ForeignKey("enabled_visitor.id"))
    id_supervisor = Column(Integer, ForeignKey("supervisor.id"))
    
    access_reason = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)
    access_time = relationship("AccessTime", uselist=False, back_populates="access_enabled")

    id_card_type = relationship("IdCardType")
    enabled_visitor = relationship("EnabledVisitor")


class AccessDenied(Base):
    __tablename__ = "access_denied"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))
    id_card_id = Column(Integer, ForeignKey("denied_visitor.id"))
    id_supervisor = Column(Integer, ForeignKey("supervisor.id"))
    
    access_reason = Column(String, nullable=True)
    department = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)

    access_time = relationship("AccessDeniedTime", uselist=False, back_populates="access_denied")
    id_card_type = relationship("IdCardType")
    denied_visitor = relationship("DeniedVisitor")


class AccessDeniedTime(Base):
    __tablename__ = "access_denied_times"
    id = Column(Integer, primary_key=True, index=True)
    access_date = Column(DateTime, nullable=True)
    exit_date = Column(DateTime, nullable=True)

    access_denied_id = Column(Integer, ForeignKey("access_denied.id"))
    access_denied = relationship("AccessDenied", back_populates="access_time")

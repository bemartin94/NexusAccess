from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
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
    id_card = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    picture = Column(String, nullable=True)

    supervisor_id = Column(Integer, ForeignKey("supervisors.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))

    id_card_type = relationship("IdCardType", back_populates="visitors")
    supervisor = relationship("Supervisor", back_populates="visitors")


class AccessTime(Base):
    __tablename__ = "access_times"
    id = Column(Integer, primary_key=True, index=True)
    access_date = Column(DateTime, nullable=True)
    exit_date = Column(DateTime, nullable=True)

    access_id = Column(Integer, ForeignKey("accesses.id"))
    access = relationship("Access", back_populates="access_time")


class Access(Base):
    __tablename__ = "accesses"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=True)
    id_card_type_id = Column(Integer, ForeignKey("id_card_types.id"))
    id_supervisor = Column(Integer, ForeignKey("supervisors.id"))
    
    access_reason = Column(String, nullable=True)
    department = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)
    status = Column(String, nullable=False)

    access_time = relationship("AccessTime", uselist=False, back_populates="access")
    id_card_type = relationship("IdCardType")
    visitor = relationship("Visitor")


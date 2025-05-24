from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Time, Date
from sqlalchemy.orm import relationship
from .database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))

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
    supervisor_id = Column(Integer, ForeignKey("supervisor.id"))


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="roles")

class Supervisor(Base): 
    __tablename__ = "supervisor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))

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



"""pensamos como alternativa eliminar las clases deniedvisitor y accessdenied,
 que la clase se llame simplemente Visitor
y agregar un campo en la clase Visitor que sea is_enabled"""
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


class AccessEnabled(Base):
    __tablename__ = "access_enabled"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("enabled_visitor.id")) 
    id_card_id = Column(Integer, ForeignKey("enabled_visitor.id")) #acá hay que marcar que se vincula con multiples tablas
    id_supervisor = Column(Integer, ForeignKey("supervisor.id"))
    access_date = Column(String, nullable=True) #esto se tiene que vincular con la tabla auxiliar
    exit_date = Column(String, nullable=True) #esto se tiene que vincular con la tabla auxiliar
    access_reason = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)
    
class AccessDenied(Base):
    __tablename__ = "access_denied"
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    id_card_type_id = Column(Integer, ForeignKey("denied_visitor.id")) 
    id_card_id = Column(Integer, ForeignKey("denied_visitor.id")) #acá hay que marcar que se vincula con multiples tablas
    id_supervisor = Column(Integer, ForeignKey("supervisor.id"))
    access_date = Column(String, nullable=True) #esto se tiene que vincular con la tabla auxiliar
    exit_date = Column(String, nullable=True) #esto se tiene que vincular con la tabla auxiliar
    access_reason = Column(String, nullable=True)
    department = Column(String, nullable=True)
    is_recurrent = Column(Boolean, nullable=True)


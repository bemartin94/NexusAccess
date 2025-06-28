from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class VenueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100) 
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    main_supervisor_user_id: Optional[int] = None # ID del usuario que es el supervisor principal

    class Config:
        from_attributes = True

class VenueCreate(VenueBase):
    pass

class VenueUpdate(VenueBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    # Todos los demás campos pueden ser Optional para la actualización

class VenueResponse(VenueBase):
    id: int
    main_supervisor_user_email: Optional[EmailStr] = None # Para mostrar el email del supervisor
    
    class Config:
        from_attributes = True
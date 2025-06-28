from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update
from typing import List, Optional

from core.models import Venue, User
from app.venues.schemas import VenueCreate, VenueUpdate

class VenueDAL:
    def __init__(self, db: AsyncSession): 
        self.db = db

    async def get_venue_by_id(self, venue_id: int) -> Optional[Venue]:
        result = await self.db.execute( 
            select(Venue)
            .options(joinedload(Venue.main_supervisor_user))
            .where(Venue.id == venue_id)
        )
        return result.scalars().first()

    async def get_venue_by_name(self, name: str) -> Optional[Venue]:
        result = await self.db.execute( 
            select(Venue)
            .options(joinedload(Venue.main_supervisor_user))
            .where(Venue.name == name)
        )
        return result.scalars().first()

    async def get_venues(self, skip: int = 0, limit: int = 100) -> List[Venue]:
        result = await self.db.execute( 
            select(Venue)
            .options(joinedload(Venue.main_supervisor_user))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create_venue(self, venue_data: VenueCreate) -> Venue:
        new_venue = Venue(
            name=venue_data.name,
            address=venue_data.address,
            city=venue_data.city,
            state=venue_data.state,
            country=venue_data.country,
            phone=venue_data.phone,
            timezone=venue_data.timezone,
            main_supervisor_user_id=venue_data.main_supervisor_user_id
        )
        self.db.add(new_venue)
        await self.db.commit() 
        await self.db.refresh(new_venue) 
        return new_venue

    async def update_venue(self, venue_id: int, venue_data: VenueUpdate) -> Optional[Venue]:
        venue_to_update = await self.get_venue_by_id(venue_id)
        if not venue_to_update:
            return None
        
        update_data = venue_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venue_to_update, key, value)
            
        await self.db.commit() 
        await self.db.refresh(venue_to_update) 
        return venue_to_update

    async def delete_venue(self, venue_id: int) -> bool:
        venue_to_delete = await self.get_venue_by_id(venue_id)
        if venue_to_delete:
            await self.db.delete(venue_to_delete) 
            await self.db.commit() 
            return True
        return False
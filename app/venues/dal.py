from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import Venue
from app.venues.schemas import VenueCreate, VenueUpdate, VenueResponse

class VenueDAL:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_venue(self, venue_create: VenueCreate) -> VenueResponse:
        venue = Venue(**venue_create.model_dump(exclude_unset=True))
        self.db.add(venue)
        await self.db.commit()
        await self.db.refresh(venue)
        return VenueResponse.model_validate(venue)

    async def get_venue_by_id(self, venue_id: int) -> Venue | None:
        result = await self.db.execute(select(Venue).filter(Venue.id == venue_id))
        return result.scalars().first()

    async def update_venue(self, venue_id: int, venue_update: VenueUpdate) -> VenueResponse | None:
        venue = await self.get_venue_by_id(venue_id)
        if not venue:
            return None

        update_data = venue_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venue, key, value)
        await self.db.commit()
        await self.db.refresh(venue)
        return VenueResponse.model_validate(venue)

    async def delete_venue(self, venue_id: int) -> bool:
        venue = await self.get_venue_by_id(venue_id)
        if not venue:
            return False
        await self.db.delete(venue)
        await self.db.commit()
        return True

    async def list_venues(self, skip: int = 0, limit: int = 100) -> list[VenueResponse]:
        result = await self.db.execute(select(Venue).offset(skip).limit(limit))
        venues = result.scalars().all()
        return [VenueResponse.model_validate(v) for v in venues]

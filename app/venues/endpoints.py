from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.venues.schemas import VenueCreate, VenueUpdate, VenueResponse
from app.venues.dal import VenueDAL
from core.database import AsyncSessionLocal  

router = APIRouter(tags=["Venues"])

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_create: VenueCreate,
    db: AsyncSession = Depends(get_db)
):
    dal = VenueDAL(db)
    venue = await dal.create_venue(venue_create)
    return VenueResponse.model_validate(venue)

@router.get("/{venue_id}", response_model=VenueResponse)
async def read_venue(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    dal = VenueDAL(db)
    venue = await dal.get_venue_by_id(venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return VenueResponse.model_validate(venue)

@router.patch("/{venue_id}", response_model=VenueResponse)
async def update_venue(
    venue_id: int,
    venue_update: VenueUpdate,
    db: AsyncSession = Depends(get_db)
):
    dal = VenueDAL(db)
    venue = await dal.update_venue(venue_id, venue_update)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return VenueResponse.model_validate(venue)

@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    dal = VenueDAL(db)
    success = await dal.delete_venue(venue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Venue not found")
    return None

@router.get("/", response_model=List[VenueResponse])
async def list_venues(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    dal = VenueDAL(db)
    venues = await dal.list_venues(skip=skip, limit=limit)
    return [VenueResponse.model_validate(venue) for venue in venues]

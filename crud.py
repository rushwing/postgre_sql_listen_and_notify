from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import TestStation
from schemas import TestStationCreate, TestStationUpdate
import uuid
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Create a new station
async def create_station(db: AsyncSession, station_data: TestStationCreate):
    try:
        logger.debug("Creating new station with name: %s", station_data.station_name)
        new_station = TestStation(
            station_name=station_data.station_name,
            station_description=station_data.station_description
        )
        db.add(new_station)
        logger.debug("Adding new station to the session.")
        await db.commit()
        logger.debug("Committed new station to the database.")
        await db.refresh(new_station)
        logger.debug("Refreshed new station instance.")
        return new_station
    except Exception as e:
        logger.error(f"Error inserting station: {e}")
        await db.rollback()
        raise e


# Get a station by ID
# Async get_station_by_id function
async def get_station_by_id(db: AsyncSession, station_id: uuid.UUID):
    result = await db.execute(select(TestStation).filter(station_id == TestStation.id))
    return result.scalars().first()  # Return the first result


# Update a station
async def update_station(db: AsyncSession, station_id: uuid.UUID, station_data: TestStationUpdate):
    station = get_station_by_id(db, station_id)
    if station:
        station.station_name = station_data.station_name
        station.station_description = station_data.station_description
        await db.commit()
        await db.refresh(station)
    return station


# Delete a station
async def delete_station(db: AsyncSession, station_id: uuid.UUID):
    station = get_station_by_id(db, station_id)
    if station:
        await db.delete(station)
        await db.commit()
    return station

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/stations/", response_model=schemas.TestStation)
async def create_station(station: schemas.TestStationCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating station: {station}")
    return await crud.create_station(db, station)


@router.get("/stations/{station_id}", response_model=schemas.TestStation)
async def read_station(station_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    db_station = await crud.get_station_by_id(db, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station


@router.put("/stations/{station_id}", response_model=schemas.TestStation)
async def update_station(station_id: uuid.UUID, station: schemas.TestStationUpdate, db: AsyncSession = Depends(get_db)):
    db_station = await crud.update_station(db, station_id, station)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    return db_station


@router.delete("/stations/{station_id}")
async def delete_station(station_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    db_station = await crud.get_station_by_id(db, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")
    await crud.delete_station(db, station_id)
    return {"message": "Station deleted successfully"}

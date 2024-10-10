from pydantic import BaseModel
import uuid


class TestStationBase(BaseModel):
    station_name: str
    station_description: str = None


class TestStationCreate(TestStationBase):
    pass


class TestStationUpdate(TestStationBase):
    pass


class TestStation(TestStationBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

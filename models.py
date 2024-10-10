import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class TestStation(Base):
    __tablename__ = "test_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    station_name = Column(String, nullable=False)
    station_description = Column(String, nullable=True)

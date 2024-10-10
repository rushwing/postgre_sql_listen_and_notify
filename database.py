from typing import AsyncGenerator, Generator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DATABASE_URL = "postgresql://tsd_harbor:tsd_harbor@localhost/test_stations"

# engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_engine = create_async_engine(
    URL.create("postgresql+asyncpg",
               username="tsd_harbor",
               password="tsd_harbor",
               host="localhost",
               port=5432,
               database="test_stations")
)
# Adjust your async session creation
async_session = async_sessionmaker(
    bind=async_engine,  # Make sure this is your async engine created earlier
    expire_on_commit=False,
    class_=AsyncSession
)


async def init_db():
    # 通过 metadata.create_all() 来创建数据库表，如果表已经存在则不会执行任何操作
    logger.info("Initializing database...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


# Dependency to get the DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

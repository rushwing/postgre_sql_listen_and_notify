import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api.main import api_router
from database import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup: initialize the database
    logger.info("Starting up the application and initializing the database...")
    await init_db()

    # Control passes here to the app during its runtime
    yield

    # Application shutdown: cleanup, close connections, etc.
    logger.info("Shutting down the application and cleaning up resources...")
    # You can add any cleanup tasks here, e.g., closing DB connections, clearing caches, etc.


fapp = FastAPI(lifespan=lifespan)
fapp.include_router(api_router)
print(fapp.routes)


if __name__ == '__main__':
    # Create the database tables
    asyncio.run(init_db())
    uvicorn.run("main:fapp", host='127.0.0.1', port=8000, reload=True)

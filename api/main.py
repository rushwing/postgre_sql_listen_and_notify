from fastapi import APIRouter

from api.routes import stations

api_router = APIRouter()
api_router.include_router(stations.router, tags=["stations"])

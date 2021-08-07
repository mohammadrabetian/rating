from fastapi import APIRouter

from app.api.api_v1.endpoints import conversion, ping, rate

api_router = APIRouter()

api_router.include_router(ping.router)
api_router.include_router(conversion.router, tags=["conversion"])
api_router.include_router(rate.router, tags=["rate"])

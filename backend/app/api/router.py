from fastapi import APIRouter

from app.api.routes import auth, bookings, health, rooms

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(rooms.router)
api_router.include_router(bookings.router)

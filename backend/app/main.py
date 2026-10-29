from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="Campus Booking API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.include_router(api_router)

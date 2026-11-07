from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: DbSession, response: Response) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError, TimeoutError):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "ok", "db": "error"}
    return {"status": "ok", "db": "ok"}

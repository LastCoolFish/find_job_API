from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from db.engine import engine
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    The `/health` endpoint reports API liveness and database connectivity.

    :return: status of the API and the database, or 503 if the database is unreachable
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {"status": "ok", "database": "ok"}

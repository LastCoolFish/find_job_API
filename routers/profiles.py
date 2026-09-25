from fastapi import APIRouter

from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])

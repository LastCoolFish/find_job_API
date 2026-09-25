from fastapi import FastAPI

from logging_config import get_logger
from routers.analytics import router as analytics_router
from routers.events import router as events_router
from routers.orders import router as orders_router
from routers.skills import router as skills_router
from routers.vacancies import router as vacancies_router

logger = get_logger(__name__)

app = FastAPI()

app.include_router(analytics_router)
app.include_router(events_router)
app.include_router(orders_router)
app.include_router(skills_router)
app.include_router(vacancies_router)

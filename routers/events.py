from typing import Annotated

from fastapi import APIRouter, Depends, Query

from db.models.EventModel import EventTarget
from logging_config import get_logger
from repositories.EventRepository import EventRepository
from schemas.event import EventCreate, EventOutSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/events", tags=["events"])

EventRepoDep = Annotated[EventRepository, Depends()]


@router.post("", status_code=201)
async def create_event(event_data: EventCreate, event_repository: EventRepoDep) -> EventOutSchema:
    """
    The `/events` POST endpoint records a user interaction event
    (view start/end, link click, search).

    :param event_data: EventCreate - event data
    :param event_repository: Depends(EventRepository)
    :return: the created event
    """
    logger.info(f"Creating event user_id={event_data.user_id} event_type={event_data.event_type}")
    event = await event_repository.create(**event_data.model_dump())
    return EventOutSchema.model_validate(event)


@router.get("/orders-views")
async def get_orders_views(
    order_ids: Annotated[list[int], Query()], event_repository: EventRepoDep
) -> dict[int, int]:
    """
    The `/events/orders-views` endpoint returns the VIEW_START count per order,
    in one query for the whole list.

    :param order_ids: ids of the orders to count views for
    :param event_repository: Depends(EventRepository)
    :return: dict of {order_id: view_count}; orders with no views get 0
    """
    logger.info(f"Fetching order views order_ids={order_ids}")
    return await event_repository.get_views(EventTarget.ORDER, order_ids)


@router.get("/vacancies-views")
async def get_vacancies_views(
    vacancies_ids: Annotated[list[int], Query()], event_repository: EventRepoDep
) -> dict[int, int]:
    """
    The `/events/vacancies-views` endpoint returns the VIEW_START count per vacancy,
    in one query for the whole list.

    :param vacancies_ids: ids of the vacancies to count views for
    :param event_repository: Depends(EventRepository)
    :return: dict of {vacancy_id: view_count}; vacancies with no views get 0
    """
    logger.info(f"Fetching vacancy views vacancies_ids={vacancies_ids}")
    return await event_repository.get_views(EventTarget.VACANCY, vacancies_ids)

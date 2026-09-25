from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.EventModel import EventModel, EventTypeEnum
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class EventRepository(BaseRepository[EventModel]):
    model = EventModel

    @request
    async def get_orders_views(self, order_ids: list[int], session: AsyncSession) -> dict[int, int]:
        """
        Returns the VIEW_START count per order for all given order ids in a single query,
        instead of one query per order.

        :param order_ids: ids of the orders to count views for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: dict of {order_id: view_count}; orders with no views get 0
        """
        query = (
            select(func.count().label("views"), EventModel.order_id)
            .where(
                EventModel.order_id.in_(order_ids),
                EventModel.event_type == EventTypeEnum.VIEW_START,
            )
            .group_by(EventModel.order_id)
        )
        result = await session.execute(query)
        views_by_order = {order_id: views for views, order_id in result.all()}

        return {order_id: views_by_order.get(order_id, 0) for order_id in order_ids}

    @request
    async def get_vacancies_views(self, vacancies_ids: list[int], session: AsyncSession) -> dict[int, int]:
        """
        Returns the VIEW_START count per vacancy for all given vacancy ids in a single query,
        instead of one query per vacancy.

        :param vacancies_ids: ids of the vacancies to count views for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: dict of {vacancy_id: view_count}; vacancies with no views get 0
        """
        query = (
            select(func.count().label("views"), EventModel.vacancy_id)
            .where(
                EventModel.vacancy_id.in_(vacancies_ids),
                EventModel.event_type == EventTypeEnum.VIEW_START,
            )
            .group_by(EventModel.vacancy_id)
        )
        result = await session.execute(query)
        views_by_vacancy = {vacancy_id: views for views, vacancy_id in result.all()}

        return {vacancy_id: views_by_vacancy.get(vacancy_id, 0) for vacancy_id in vacancies_ids}

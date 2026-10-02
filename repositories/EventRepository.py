from typing import Any

from sqlalchemy import select, func, Row
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.EventModel import EventModel, EventTarget, EventTypeEnum
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository
from schemas.common import SortOrder

logger = get_logger(__name__)

_TARGET_COLUMN = {
    EventTarget.VACANCY: EventModel.vacancy_id,
    EventTarget.ORDER: EventModel.order_id,
}


class EventRepository(BaseRepository[EventModel]):
    model = EventModel

    @request
    async def get_by_user_id(
        self,
        user_id: int,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        event_type: EventTypeEnum | None = None,
        order: SortOrder = "desc",
    ) -> tuple[list[EventModel], int]:
        """
        Returns events recorded for a user, newest first by default. \n

        :param user_id: id of the user whose events to return
        :param session: sqlalchemy.AsyncSession
        :param limit: max number of events to return, or None for no limit
        :param offset: number of matching events to skip
        :param event_type: restrict to a single event type, or None for all types
        :param order: "asc" or "desc", by occurred_at
        :return: tuple of (the user's events, total matching count)
        """
        conditions = [EventModel.user_id == user_id]
        if event_type is not None:
            conditions.append(EventModel.event_type == event_type)

        query = select(EventModel).where(*conditions)
        query = self._sort(query, EventModel.occurred_at, order)
        query = self._paginate(query, limit, offset)

        items = list((await session.execute(query)).scalars().all())
        total = await self._count(session, *conditions)
        return items, total

    @request
    async def get_views(self, target: EventTarget, ids: list[int], session: AsyncSession) -> dict[int, int]:
        """
        Returns the VIEW_START count per vacancy/order for all given ids in a single query,
        instead of one query per item.

        :param target: EventTarget.VACANCY or EventTarget.ORDER - which id column to group by
        :param ids: ids of the vacancies/orders to count views for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: dict of {id: view_count}; ids with no views get 0
        """
        column = _TARGET_COLUMN[target]
        query = (
            select(column, func.count().label("views"))
            .where(column.in_(ids), EventModel.event_type == EventTypeEnum.VIEW_START)
            .group_by(column)
        )
        counts = dict((await session.execute(query)).all())

        return {i: counts.get(i, 0) for i in ids}

    @request
    async def get_analytic_info(
        self, target: EventTarget, target_id: int, session: AsyncSession
    ) -> Row[tuple[Any, Any, Any]]:
        """
        Returns engagement analytics for a single vacancy/order: average view duration,
        number of link clicks and total views.

        :param target: EventTarget.VACANCY or EventTarget.ORDER - which id column to filter by
        :param target_id: id of the vacancy/order to compute analytics for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: Row with avg_view_duration (None if never viewed), link_clicks, total_views
        """
        column = _TARGET_COLUMN[target]
        query = select(
            func.avg(EventModel.duration_seconds).filter(
                EventModel.event_type == EventTypeEnum.VIEW_END
            ).label("avg_view_duration"),
            func.count().filter(
                EventModel.event_type == EventTypeEnum.LINK_CLICK
            ).label("link_clicks"),
            func.count().filter(
                EventModel.event_type == EventTypeEnum.VIEW_START
            ).label("total_views"),
        ).where(column == target_id)

        return (await session.execute(query)).one()

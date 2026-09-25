from typing import Any, Sequence

from sqlalchemy import select, func, Row
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models import EventModel
from db.models.CompanyModel import CompanyModel
from db.models.EventModel import EventTypeEnum
from db.models.SkillModel import SkillModel
from db.models.VacancyModel import VacancyModel
from db.models.VacancySkillModel import VacancySkillModel
from logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsRepository:
    @request
    async def get_top_skills(self, count: int = 5, *, session: AsyncSession) -> Sequence[Row[tuple[Any, Any]]]:
        """
        Returns the top most in-demand skills for job vacancies.. \n
        Accepts a `count` parameter specifying the number of output items. \n
        The default value is 5; \n
        - if the value is greater than 0, the top items from rank 1 up to the specified number are returned; \n
        - if `count` is less than 0, items from the end of the ranked list are returned; \n
        - if `count` is 0, the all ranked list is returned. \n

        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :param count: int - number of returned elements
        :return: Sequence[Row[tuple[Any, Any]]] - SkillModel + count as 'vacancy_count'
        """

        query = (select(SkillModel, func.count(VacancySkillModel.vacancy_id).label("vacancy_count"))
                 .join(VacancySkillModel, SkillModel.id == VacancySkillModel.skill_id)
                 .group_by(SkillModel.id))

        if count > 0:
            query = query.order_by(func.count().desc()).limit(count)
        elif count < 0:
            query = query.order_by(func.count()).limit(-count)
        else:
            query = query.order_by(func.count().desc())

        result = await session.execute(query)

        if count >= 0:
            return result.all()

        else:
            return result.all()[::-1]

    @request
    async def get_top_vacancy_posters(self, count: int = 5, *, session: AsyncSession) -> Sequence[Row[tuple[Any, Any]]]:
        """
        Returns the top companies offering the most vacancy posters. \n
        Accepts a `count` parameter specifying the number of output items. \n
        The default value is 5; \n
        - if the value is greater than 0, the top items from rank 1 up to the specified number are returned; \n
        - if `count` is less than 0, items from the end of the ranked list are returned; \n
        - if `count` is 0, the all ranked list is returned. \n

        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :param count: int - number of returned elements
        :return: Sequence[Row[tuple[Any, Any]]] - CompanyModel + count as 'vacancy_count'
        """

        query = (select(CompanyModel, func.count(VacancyModel.id).label("vacancy_count"))
                 .join(VacancyModel, VacancyModel.company_id == CompanyModel.id)
                 .group_by(CompanyModel.id))

        if count > 0:
            query = query.order_by(func.count().desc()).limit(count)
        elif count < 0:
            query = query.order_by(func.count()).limit(-count)
        else:
            query = query.order_by(func.count().desc())

        result = await session.execute(query)

        if count >= 0:
            return result.all()

        else:
            return result.all()[::-1]

    @request
    async def get_vacancy_analytic_info(self, vacancy_id: int, session: AsyncSession) -> dict[str, float | int | None]:
        """
        Returns engagement analytics for a single vacancy: average view duration,
        number of link clicks, total views and click-through rate (CTR).

        :param vacancy_id: id of the vacancy to compute analytics for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: dict with avg_view_duration (None if never viewed), link_clicks,
            total_views and ctr (0.0 if total_views is 0)
        """
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
        ).where(EventModel.vacancy_id == vacancy_id)

        row = (await session.execute(query)).one()

        return {
            "avg_view_duration": row.avg_view_duration,
            "link_clicks": row.link_clicks,
            "total_views": row.total_views,
            "ctr": row.link_clicks / row.total_views if row.total_views else 0.0,
        }

    @request
    async def get_order_analytic_info(self, order_id: int, session: AsyncSession) -> dict[str, float | int | None]:
        """
        Returns engagement analytics for a single order: average view duration,
        number of link clicks, total views and click-through rate (CTR).

        :param order_id: id of the order to compute analytics for
        :param session: sqlalchemy.ext.asyncio.AsyncSession
        :return: dict with avg_view_duration (None if never viewed), link_clicks,
            total_views and ctr (0.0 if total_views is 0)
        """
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
        ).where(EventModel.order_id == order_id)

        row = (await session.execute(query)).one()

        return {
            "avg_view_duration": row.avg_view_duration,
            "link_clicks": row.link_clicks,
            "total_views": row.total_views,
            "ctr": row.link_clicks / row.total_views if row.total_views else 0.0,
        }

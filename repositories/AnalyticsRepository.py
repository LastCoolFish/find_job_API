from typing import Any, Sequence

from sqlalchemy import select, func, Row
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.SkillModel import SkillModel
from db.models.VacancySkillModel import VacancySkillModel
from logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsRepository:
    @request
    async def get_top_skills(self, session: AsyncSession, count: int = 5) -> Sequence[Row[tuple[Any, Any]]]:
        """
        Returns the top skills for the job openings. \n
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

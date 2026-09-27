from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count

from db.engine import request
from db.models.SkillModel import SkillModel
from db.models.VacancyModel import VacancyModel
from db.models.VacancySkillModel import VacancySkillModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository
from schemas.common import SortOrder
from schemas.vacancy import VacancyFilterSchema, VacancySortField

logger = get_logger(__name__)

_SORTABLE_COLUMNS = {
    "id": VacancyModel.id,
    "job_title": VacancyModel.job_title,
    "salary": VacancyModel.salary,
    "grade": VacancyModel.grade,
    "place": VacancyModel.place,
}


class VacancyRepository(BaseRepository[VacancyModel]):
    model = VacancyModel

    @request
    async def get_all(
        self,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        sort_by: VacancySortField | None = None,
        order: SortOrder = "asc",
    ) -> list[VacancyModel]:
        query = select(VacancyModel).options(
            selectinload(VacancyModel.company),
            selectinload(VacancyModel.skills),
        )
        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> VacancyModel | None:
        result = await session.execute(
            select(VacancyModel)
            .where(VacancyModel.id == model_id)
            .options(
                selectinload(VacancyModel.company),
                selectinload(VacancyModel.skills),
            )
        )
        return result.scalars().one_or_none()

    @request
    async def get_by_skills(self, skills_id: list[int], session: AsyncSession) -> list[VacancyModel]:
        subquery = (select(VacancySkillModel.vacancy_id)
                 .where(VacancySkillModel.skill_id.in_(skills_id))
                 .group_by(VacancySkillModel.vacancy_id)
                 .having(count(VacancySkillModel.vacancy_id) == len(skills_id)))

        query = (
            select(VacancyModel)
            .where(VacancyModel.id.in_(subquery))
            .options(
                selectinload(VacancyModel.company),
                selectinload(VacancyModel.skills),
            )
        )

        result = await session.execute(query)
        return list(result.scalars().all())

    @request
    async def get_filtered(
        self,
        filters: VacancyFilterSchema,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        sort_by: VacancySortField | None = None,
        order: SortOrder = "asc",
    ) -> list[VacancyModel]:
        """
        Returns vacancies matching every given filter; a filter left as None is not applied. \n

        :param filters: VacancyFilterSchema - optional filter values
        :param session: sqlalchemy.AsyncSession
        :param limit: max number of vacancies to return, or None for no limit
        :param offset: number of matching vacancies to skip
        :param sort_by: column to sort by, or None to leave the result unsorted
        :param order: "asc" or "desc"
        :return: vacancies matching all provided filters
        """
        query = select(VacancyModel).options(
            selectinload(VacancyModel.company),
            selectinload(VacancyModel.skills),
        )

        if filters.job_title is not None:
            query = query.where(VacancyModel.job_title.ilike(f"%{filters.job_title}%"))
        if filters.salary_min is not None:
            query = query.where(VacancyModel.salary >= filters.salary_min)
        if filters.salary_max is not None:
            query = query.where(VacancyModel.salary <= filters.salary_max)
        if filters.place is not None:
            query = query.where(VacancyModel.place.ilike(f"%{filters.place}%"))
        if filters.grade is not None:
            query = query.where(VacancyModel.grade == filters.grade)
        if filters.format is not None:
            query = query.where(VacancyModel.format == filters.format)
        if filters.platform is not None:
            query = query.where(VacancyModel.platform == filters.platform)
        if filters.company_id is not None:
            query = query.where(VacancyModel.company_id == filters.company_id)

        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        result = await session.execute(query)
        return list(result.scalars().all())

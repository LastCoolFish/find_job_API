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

logger = get_logger(__name__)


class VacancyRepository(BaseRepository[VacancyModel]):
    model = VacancyModel

    @request
    async def get_all(self, session: AsyncSession) -> list[VacancyModel]:
        result = await session.execute(
            select(VacancyModel).options(
                selectinload(VacancyModel.company),
                selectinload(VacancyModel.skills),
            )
        )
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

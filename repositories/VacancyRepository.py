from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import request
from db.models.VacancyModel import VacancyModel
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

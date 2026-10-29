from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.SkillModel import SkillModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class SkillRepository(BaseRepository[SkillModel]):
    model = SkillModel

    @request
    async def get_by_ids(self, skill_ids: list[int], session: AsyncSession) -> list[SkillModel]:
        """
        Returns the existing skills among the given ids in a single query. \n

        :param skill_ids: ids of the skills to look up
        :param session: sqlalchemy.AsyncSession
        :return: list of found skills; ids that do not exist are simply absent
        """
        result = await session.execute(select(SkillModel).where(SkillModel.id.in_(skill_ids)))
        return list(result.scalars().all())

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.ProfileModel import ProfileModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class ProfileRepository(BaseRepository[ProfileModel]):
    model = ProfileModel

    @request
    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> ProfileModel | None:
        """
        Returns the profile by user id, or None if it does not exist. \n

        :param user_id: id of the user whose profile to return
        :param session: sqlalchemy.AsyncSession
        :return: model type (ProfileModel) | None
        """
        result = await session.execute(select(self.model).where(self.model.user_id == user_id))
        return result.scalars().one_or_none()

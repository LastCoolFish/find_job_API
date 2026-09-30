from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import request
from db.models.ProfileModel import ProfileModel
from db.models.ProfileSkillModel import ProfileSkillModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class ProfileRepository(BaseRepository[ProfileModel]):
    model = ProfileModel

    @request
    async def get_all(self, session: AsyncSession) -> list[ProfileModel]:
        result = await session.execute(
            select(ProfileModel).options(selectinload(ProfileModel.skills))
        )
        return list(result.scalars().all())

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> ProfileModel | None:
        result = await session.execute(
            select(ProfileModel)
            .where(ProfileModel.id == model_id)
            .options(selectinload(ProfileModel.skills))
        )
        return result.scalars().one_or_none()

    @request
    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> ProfileModel | None:
        """
        Returns the profile by user id, or None if it does not exist. \n

        :param user_id: id of the user whose profile to return
        :param session: sqlalchemy.AsyncSession
        :return: model type (ProfileModel) | None
        """
        result = await session.execute(
            select(ProfileModel)
            .where(ProfileModel.user_id == user_id)
            .options(selectinload(ProfileModel.skills))
        )
        return result.scalars().one_or_none()

    @request
    async def add_skill(self, profile_id: int, skill_id: int, session: AsyncSession) -> None:
        """
        Attaches a skill to a profile; a no-op if already attached. \n

        :param profile_id: id of the profile to attach the skill to
        :param skill_id: id of the skill to attach
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        stmt = (
            insert(ProfileSkillModel)
            .values(profile_id=profile_id, skill_id=skill_id)
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)

    @request
    async def remove_skill(self, profile_id: int, skill_id: int, session: AsyncSession) -> None:
        """
        Detaches a skill from a profile; a no-op if not attached. \n

        :param profile_id: id of the profile to detach the skill from
        :param skill_id: id of the skill to detach
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        await session.execute(
            delete(ProfileSkillModel).where(
                ProfileSkillModel.profile_id == profile_id,
                ProfileSkillModel.skill_id == skill_id,
            )
        )

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
    async def add_skills(self, profile_id: int, skill_ids: list[int], session: AsyncSession) -> None:
        """
        Attaches the given skills to a profile in a single statement; already attached ones are skipped. \n

        :param profile_id: id of the profile to attach the skills to
        :param skill_ids: ids of the skills to attach
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        if not skill_ids:
            return
        stmt = (
            insert(ProfileSkillModel)
            .values([{"profile_id": profile_id, "skill_id": skill_id} for skill_id in skill_ids])
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)

    @request
    async def remove_skills(self, profile_id: int, skill_ids: list[int], session: AsyncSession) -> None:
        """
        Detaches the given skills from a profile in a single statement; not attached ones are skipped. \n

        :param profile_id: id of the profile to detach the skills from
        :param skill_ids: ids of the skills to detach
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        if not skill_ids:
            return
        await session.execute(
            delete(ProfileSkillModel).where(
                ProfileSkillModel.profile_id == profile_id,
                ProfileSkillModel.skill_id.in_(skill_ids),
            )
        )

    @request
    async def set_skills(self, profile_id: int, skill_ids: list[int], session: AsyncSession) -> None:
        """
        Replaces the whole skill set of a profile with the given one (an empty list clears it);
        delete and insert run in one transaction, so a failed insert leaves the old set intact. \n

        :param profile_id: id of the profile whose skills to replace
        :param skill_ids: ids of the skills the profile must end up with
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        await session.execute(delete(ProfileSkillModel).where(ProfileSkillModel.profile_id == profile_id))
        if skill_ids:
            await session.execute(
                insert(ProfileSkillModel).values(
                    [{"profile_id": profile_id, "skill_id": skill_id} for skill_id in skill_ids]
                )
            )

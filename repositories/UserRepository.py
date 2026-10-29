from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import request
from db.models.ProfileModel import ProfileModel
from db.models.UserModel import UserModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class UserRepository(BaseRepository[UserModel]):
    model = UserModel

    @request
    async def get_by_email(self, email: str, session: AsyncSession) -> UserModel | None:
        """
        Returns the user with the given email (exact match), or None if there is none. \n

        :param email: email of the user to return
        :param session: sqlalchemy.AsyncSession
        :return: model type (UserModel) | None
        """
        result = await session.execute(select(UserModel).where(UserModel.email == email))
        return result.scalars().one_or_none()

    @request
    async def set_last_login(self, user_id: int, session: AsyncSession) -> None:
        """
        Stamps `last_login_at` with the current time. `updated_at` is deliberately kept
        as is, so signing in doesn't count as a change to the user's data. \n

        :param user_id: id of the user who just signed in
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        await session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(last_login_at=func.now(), updated_at=UserModel.updated_at)
        )

    @request
    async def create_with_profile(
            self, user_data: dict, profile_data: dict, session: AsyncSession
    ) -> UserModel:
        """
        Creates a user together with their profile in a single transaction: if either
        insert fails (e.g. duplicate email or username), neither is saved. \n
        If `profile_data` has no username, one is generated as `user_{user_id}`.

        :param user_data: columns of the new user (email, phone, hashed_password, ...)
        :param profile_data: columns of the new profile, without user_id
        :param session: sqlalchemy.AsyncSession
        :return: the created user with its profile (and the profile's skills) loaded
        """
        user = UserModel(**user_data)
        session.add(user)
        await session.flush()

        profile_data = {**profile_data, "username": profile_data.get("username") or f"user_{user.id}"}
        session.add(ProfileModel(user_id=user.id, **profile_data))
        await session.flush()

        result = await session.execute(
            select(UserModel)
            .where(UserModel.id == user.id)
            .options(selectinload(UserModel.profile).selectinload(ProfileModel.skills))
            .execution_options(populate_existing=True)
        )
        return result.scalars().one()

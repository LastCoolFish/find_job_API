from datetime import timedelta

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request
from db.models.RefreshTokenModel import RefreshTokenModel
from db.models.UserModel import RoleEnum, UserModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


async def _revoke_family(session: AsyncSession, family_id: str) -> None:
    await session.execute(
        update(RefreshTokenModel)
        .where(RefreshTokenModel.family_id == family_id, RefreshTokenModel.revoked_at.is_(None))
        .values(revoked_at=func.now())
    )


class RefreshTokenRepository(BaseRepository[RefreshTokenModel]):
    model = RefreshTokenModel

    @request
    async def issue(
            self, user_id: int, token_hash: str, family_id: str, lifetime: timedelta, session: AsyncSession
    ) -> None:
        """
        Stores a new refresh token (by hash). Expiry is computed with the database clock. \n

        :param user_id: id of the user the token belongs to
        :param token_hash: SHA-256 of the token
        :param family_id: id of the login session this token belongs to
        :param lifetime: how long the token stays valid
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        session.add(
            RefreshTokenModel(
                user_id=user_id,
                token_hash=token_hash,
                family_id=family_id,
                expires_at=func.now() + lifetime,
            )
        )

    @request
    async def rotate(
            self, token_hash: str, new_token_hash: str, lifetime: timedelta, session: AsyncSession
    ) -> int | None:
        """
        Exchanges a refresh token for a new one in a single transaction: the old token is
        marked used and the new one (same family) is stored. The old row is locked, so two
        simultaneous requests with the same token can't both succeed. \n
        Nothing is rotated, and None is returned, when the token is unknown, expired, or its
        user is blocked. If the token was already used or revoked, someone is replaying it
        (or it was stolen): the whole family is revoked, which logs that session out. \n

        :param token_hash: SHA-256 of the presented refresh token
        :param new_token_hash: SHA-256 of the replacement token
        :param lifetime: how long the new token stays valid
        :param session: sqlalchemy.AsyncSession
        :return: id of the user the tokens belong to, or None if the token can't be used
        """
        result = await session.execute(
            select(RefreshTokenModel, RefreshTokenModel.expires_at <= func.now(), UserModel.role)
            .join(UserModel, UserModel.id == RefreshTokenModel.user_id)
            .where(RefreshTokenModel.token_hash == token_hash)
            .with_for_update(of=RefreshTokenModel)
        )
        row = result.one_or_none()
        if row is None:
            logger.warning("Refresh with an unknown token")
            return None

        token, expired, role = row
        if token.revoked_at is not None:
            logger.warning(f"Refresh token reuse user_id={token.user_id} family={token.family_id}; revoking the family")
            await _revoke_family(session, token.family_id)
            return None
        if expired:
            logger.warning(f"Refresh with an expired token user_id={token.user_id}")
            return None
        if role == RoleEnum.BLOCKED:
            logger.warning(f"Blocked user id={token.user_id} tried to refresh; revoking the family")
            await _revoke_family(session, token.family_id)
            return None

        token.revoked_at = func.now()
        session.add(
            RefreshTokenModel(
                user_id=token.user_id,
                token_hash=new_token_hash,
                family_id=token.family_id,
                expires_at=func.now() + lifetime,
            )
        )
        return token.user_id

    @request
    async def revoke_session(self, token_hash: str, session: AsyncSession) -> None:
        """
        Logs out the session the token belongs to by revoking its whole family. Idempotent:
        an unknown or already revoked token is silently ignored. \n

        :param token_hash: SHA-256 of the refresh token
        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        family_id = await session.scalar(
            select(RefreshTokenModel.family_id).where(RefreshTokenModel.token_hash == token_hash)
        )
        if family_id is not None:
            await _revoke_family(session, family_id)

    @request
    async def delete_expired(self, session: AsyncSession) -> None:
        """
        Deletes refresh tokens that have expired (they're useless, used up or not). \n

        :param session: sqlalchemy.AsyncSession
        :return: None
        """
        await session.execute(delete(RefreshTokenModel).where(RefreshTokenModel.expires_at < func.now()))

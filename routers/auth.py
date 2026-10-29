from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from db.models.UserModel import RoleEnum
from dependencies import CurrentUser
from logging_config import get_logger
from repositories.RefreshTokenRepository import RefreshTokenRepository
from repositories.UserRepository import UserRepository
from schemas.auth import LoginSchema, RefreshTokenSchema, TokenSchema
from schemas.user import UserOutSchema
from security import (
    REFRESH_TOKEN_LIFETIME,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

UserRepoDep = Annotated[UserRepository, Depends()]
RefreshTokenRepoDep = Annotated[RefreshTokenRepository, Depends()]


@router.post("/login")
async def login(
        payload: LoginSchema, user_repository: UserRepoDep, refresh_token_repository: RefreshTokenRepoDep
) -> TokenSchema:
    """
    The `/auth/login` endpoint exchanges an email and password for a short-lived access
    token (send it as `Authorization: Bearer <token>`) and a long-lived refresh token
    (send it to `/auth/refresh` to get a new pair). \n
    An unknown email and a wrong password give the same 401, so the response doesn't
    reveal which emails are registered.

    :param payload: LoginSchema - email and password
    :param user_repository: Depends(UserRepository)
    :param refresh_token_repository: Depends(RefreshTokenRepository)
    :return: the token pair; 401 on wrong credentials, 403 if the account is blocked
    """
    logger.info(f"Login attempt email={payload.email!r}")
    user = await user_repository.get_by_email(payload.email)
    password_ok = await verify_password(
        payload.password.get_secret_value(), user.hashed_password if user else None
    )
    if user is None or not password_ok:
        logger.warning(f"Failed login email={payload.email!r}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.role == RoleEnum.BLOCKED:
        logger.warning(f"Blocked user id={user.id} tried to log in")
        raise HTTPException(status_code=403, detail="Account is blocked")

    await user_repository.set_last_login(user.id)

    # Housekeeping: expired refresh tokens are dropped on login, so no scheduler is needed.
    await refresh_token_repository.delete_expired()
    refresh_token = create_refresh_token()
    await refresh_token_repository.issue(
        user.id, hash_refresh_token(refresh_token), uuid4().hex, REFRESH_TOKEN_LIFETIME
    )
    return TokenSchema(access_token=create_access_token(str(user.id)), refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(payload: RefreshTokenSchema, refresh_token_repository: RefreshTokenRepoDep) -> TokenSchema:
    """
    The `/auth/refresh` endpoint exchanges a refresh token for a new access token and a
    new refresh token. Refresh tokens are single-use: the one you send stops working. \n
    Sending an already used one is treated as a replay and ends the whole login session,
    so every token of that session is revoked and the user has to log in again.

    :param payload: RefreshTokenSchema - the refresh token from login or the previous refresh
    :param refresh_token_repository: Depends(RefreshTokenRepository)
    :return: a new token pair; 401 if the token is unknown, expired, used or revoked
    """
    new_refresh_token = create_refresh_token()
    user_id = await refresh_token_repository.rotate(
        hash_refresh_token(payload.refresh_token),
        hash_refresh_token(new_refresh_token),
        REFRESH_TOKEN_LIFETIME,
    )
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenSchema(access_token=create_access_token(str(user_id)), refresh_token=new_refresh_token)


@router.post("/logout", status_code=204)
async def logout(payload: RefreshTokenSchema, refresh_token_repository: RefreshTokenRepoDep) -> None:
    """
    The `/auth/logout` endpoint ends the login session the refresh token belongs to:
    that token and every later one from the same login stop working. Other devices,
    which logged in separately, stay signed in. \n
    It always answers 204, even for an unknown token, so it can't be used to probe tokens.
    The already issued access token stays valid until it expires.

    :param payload: RefreshTokenSchema - the refresh token of the session to end
    :param refresh_token_repository: Depends(RefreshTokenRepository)
    :return: None
    """
    await refresh_token_repository.revoke_session(hash_refresh_token(payload.refresh_token))


@router.get("/me")
async def get_me(current_user: CurrentUser) -> UserOutSchema:
    """
    The `/auth/me` endpoint returns the user the access token belongs to.

    :param current_user: Depends(get_current_user)
    :return: the authenticated user
    """
    return UserOutSchema.model_validate(current_user)

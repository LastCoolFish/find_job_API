from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.models.ProfileModel import ProfileModel
from db.models.UserModel import RoleEnum, UserModel
from logging_config import get_logger
from repositories.ProfileRepository import ProfileRepository
from repositories.UserRepository import UserRepository
from security import decode_access_token

logger = get_logger(__name__)

# auto_error=False: a missing header is turned into our own 401 below, so every auth failure looks the same.
bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
        user_repository: Annotated[UserRepository, Depends()],
) -> UserModel:
    """
    Resolves the user behind the `Authorization: Bearer <token>` header.

    :param credentials: Depends(HTTPBearer) - the bearer token from the request
    :param user_repository: Depends(UserRepository)
    :return: the authenticated user; 401 if the token is missing, invalid or expired,
        or the user no longer exists; 403 if the user is blocked
    """
    if credentials is None:
        raise _unauthorized()

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise _unauthorized()

    try:
        user_id = int(payload["sub"])
    except ValueError:
        raise _unauthorized()

    user = await user_repository.get_by_id(user_id)
    if user is None:
        logger.warning(f"Token for missing user id={user_id}")
        raise _unauthorized()
    if user.role == RoleEnum.BLOCKED:
        logger.warning(f"Blocked user id={user_id} tried to use a token")
        raise HTTPException(status_code=403, detail="Account is blocked")
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]


async def require_admin(current_user: CurrentUser) -> UserModel:
    """
    Lets only admins through.

    :param current_user: Depends(get_current_user)
    :return: the authenticated admin user; 403 for any other role
    """
    if current_user.role != RoleEnum.ADMIN:
        logger.warning(f"User id={current_user.id} tried an admin-only action")
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


AdminUser = Annotated[UserModel, Depends(require_admin)]


async def require_self(user_id: int, current_user: CurrentUser) -> UserModel:
    """
    Lets a user through only to their own resource. `user_id` is the `{user_id}` path
    parameter of the route this is attached to.

    :param user_id: id of the user the request is about (from the path)
    :param current_user: Depends(get_current_user)
    :return: the authenticated user; 403 if they are not the user in the path
    """
    if current_user.id != user_id:
        logger.warning(f"User id={current_user.id} tried to access user id={user_id}")
        raise HTTPException(status_code=403, detail="You can only access your own account")
    return current_user


async def get_owned_profile(
        profile_id: int,
        current_user: CurrentUser,
        profile_repository: Annotated[ProfileRepository, Depends()],
) -> ProfileModel:
    """
    Lets a user through only to their own profile. `profile_id` is the `{profile_id}` path
    parameter of the route this is attached to.

    :param profile_id: id of the profile the request is about (from the path)
    :param current_user: Depends(get_current_user)
    :param profile_repository: Depends(ProfileRepository)
    :return: the profile (with its skills loaded); 404 if it doesn't exist,
        403 if it belongs to someone else
    """
    profile = await profile_repository.get_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.user_id != current_user.id:
        logger.warning(f"User id={current_user.id} tried to use profile id={profile_id} of user id={profile.user_id}")
        raise HTTPException(status_code=403, detail="You can only manage your own profile")
    return profile

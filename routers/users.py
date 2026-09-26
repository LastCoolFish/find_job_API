from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.UserRepository import UserRepository
from schemas.user import UserCreateSchema, UserOutSchema, UserUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

UserRepoDep = Annotated[UserRepository, Depends()]


@router.get("")
async def get_all_users(user_repository: UserRepoDep) -> list[UserOutSchema]:
    """
    The base endpoint `/users` returns all users.

    :param user_repository: Depends(UserRepository)
    :return: all users
    """
    logger.info("Fetching all users")
    users = await user_repository.get_all()
    return [UserOutSchema.model_validate(user) for user in users]


@router.get("/{user_id}")
async def get_user(user_id: int, user_repository: UserRepoDep) -> UserOutSchema:
    """
    The `/users/{user_id}` endpoint returns a single user by id.

    :param user_id: id of the user to return
    :param user_repository: Depends(UserRepository)
    :return: the user, or 404 if it does not exist
    """
    logger.info(f"Fetching user id={user_id}")
    user = await user_repository.get_by_id(user_id)
    if user is None:
        logger.warning(f"User id={user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserOutSchema.model_validate(user)


@router.post("", status_code=201)
async def create_user(payload: UserCreateSchema, user_repository: UserRepoDep) -> UserOutSchema:
    """
    The `/users` POST endpoint creates a new user.

    :param payload: UserCreateSchema - data of the new user
    :param user_repository: Depends(UserRepository)
    :return: the created user
    """
    logger.info(f"Creating user email={payload.email!r}")
    user = await user_repository.create(**payload.model_dump())
    return UserOutSchema.model_validate(user)


@router.put("/{user_id}")
async def update_user(user_id: int, payload: UserUpdateSchema, user_repository: UserRepoDep) -> UserOutSchema:
    """
    The `/users/{user_id}` PUT endpoint updates an existing user.

    :param user_id: id of the user to update
    :param payload: UserUpdateSchema - fields to update
    :param user_repository: Depends(UserRepository)
    :return: the updated user, or 404 if it does not exist
    """
    logger.info(f"Updating user id={user_id}")
    user = await user_repository.update_by_id(user_id, **payload.model_dump(exclude_unset=True))
    if user is None:
        logger.warning(f"User id={user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return UserOutSchema.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, user_repository: UserRepoDep) -> None:
    """
    The `/users/{user_id}` DELETE endpoint deletes a user by id.

    :param user_id: id of the user to delete
    :param user_repository: Depends(UserRepository)
    :return: None
    """
    logger.info(f"Deleting user id={user_id}")
    user = await user_repository.delete_by_id(user_id)
    if user is None:
        logger.warning(f"User id={user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from db.models.EventModel import EventTypeEnum
from logging_config import get_logger
from repositories.EventRepository import EventRepository
from repositories.UserRepository import UserRepository
from schemas.common import PaginatedResponse, SortOrder
from schemas.event import EventOutSchema
from schemas.user import UserCreateSchema, UserOutSchema, UserUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

UserRepoDep = Annotated[UserRepository, Depends()]
EventRepoDep = Annotated[EventRepository, Depends()]


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


@router.get("/{user_id}/events")
async def get_user_events(
        user_id: int,
        user_repository: UserRepoDep,
        event_repository: EventRepoDep,
        event_type: EventTypeEnum | None = None,
        limit: Annotated[int | None, Query(ge=1, le=100)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        order: SortOrder = "desc",
) -> PaginatedResponse[EventOutSchema]:
    """
    The `/users/{user_id}/events` endpoint returns the user's recorded activity
    (view start/end, link click, search), newest first by default.

    :param user_id: id of the user whose events to return
    :param user_repository: Depends(UserRepository)
    :param event_repository: Depends(EventRepository)
    :param event_type: restrict to a single event type, or None for all types
    :param limit: max number of events to return, or None for no limit
    :param offset: number of matching events to skip
    :param order: "asc" or "desc", by occurred_at
    :return: the user's events, or 404 if the user does not exist
    """
    user = await user_repository.get_by_id(user_id)
    if user is None:
        logger.warning(f"User id={user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(
        f"Fetching events user_id={user_id} event_type={event_type} "
        f"limit={limit} offset={offset} order={order}"
    )
    events, total = await event_repository.get_by_user_id(
        user_id, limit=limit, offset=offset, event_type=event_type, order=order
    )
    return PaginatedResponse(
        items=[EventOutSchema.model_validate(event) for event in events],
        total=total,
        limit=limit,
        offset=offset,
    )


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

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError

from db.models.EventModel import EventTypeEnum
from dependencies import require_admin, require_self
from logging_config import get_logger
from repositories.EventRepository import EventRepository
from repositories.UserRepository import UserRepository
from schemas.common import PaginatedResponse, SortOrder
from schemas.event import EventOutSchema
from schemas.user import UserCreateSchema, UserOutSchema, UserUpdateSchema, UserWithProfileOutSchema
from security import hash_password

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

UserRepoDep = Annotated[UserRepository, Depends()]
EventRepoDep = Annotated[EventRepository, Depends()]


@router.get("", dependencies=[Depends(require_admin)])
async def get_all_users(user_repository: UserRepoDep) -> list[UserOutSchema]:
    """
    The base endpoint `/users` returns all users.

    Access: admins only.

    :param user_repository: Depends(UserRepository)
    :return: all users
    """
    logger.info("Fetching all users")
    users = await user_repository.get_all()
    return [UserOutSchema.model_validate(user) for user in users]


@router.get("/{user_id}", dependencies=[Depends(require_self)])
async def get_user(user_id: int, user_repository: UserRepoDep) -> UserOutSchema:
    """
    The `/users/{user_id}` endpoint returns a single user by id.

    Access: only the user themselves.

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


@router.get("/{user_id}/events", dependencies=[Depends(require_admin)])
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

    Access: admins only.

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
async def create_user(payload: UserCreateSchema, user_repository: UserRepoDep) -> UserWithProfileOutSchema:
    """
    The `/users` POST endpoint registers a new user together with their profile in one
    transaction. The password is stored only as a bcrypt hash; the role is always the
    default (`user`) and cannot be set here. If the profile has no username, one is
    generated from the user id.

    :param payload: UserCreateSchema - email, phone, password and optional profile data
    :param user_repository: Depends(UserRepository)
    :return: the created user with their profile, or 409 if the email or username is taken
    """
    logger.info(f"Creating user email={payload.email!r}")
    hashed_password = await hash_password(payload.password.get_secret_value())
    try:
        user = await user_repository.create_with_profile(
            user_data={"email": payload.email, "phone": payload.phone, "hashed_password": hashed_password},
            profile_data=payload.profile.model_dump(),
        )
    except IntegrityError:
        logger.warning(f"User email={payload.email!r} or its username already exists")
        raise HTTPException(status_code=409, detail="User with this email or username already exists")
    return UserWithProfileOutSchema.model_validate(user)


@router.put("/{user_id}", dependencies=[Depends(require_admin)])
async def update_user(user_id: int, payload: UserUpdateSchema, user_repository: UserRepoDep) -> UserOutSchema:
    """
    The `/users/{user_id}` PUT endpoint updates an existing user.

    Access: admins only.

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


@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_user(user_id: int, user_repository: UserRepoDep) -> None:
    """
    The `/users/{user_id}` DELETE endpoint deletes a user by id.

    Access: admins only.

    :param user_id: id of the user to delete
    :param user_repository: Depends(UserRepository)
    :return: None
    """
    logger.info(f"Deleting user id={user_id}")
    user = await user_repository.delete_by_id(user_id)
    if user is None:
        logger.warning(f"User id={user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

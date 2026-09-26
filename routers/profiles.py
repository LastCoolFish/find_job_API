from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.ProfileRepository import ProfileRepository
from schemas.profile import ProfileCreateSchema, ProfileOutSchema, ProfileUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])

ProfileRepoDep = Annotated[ProfileRepository, Depends()]


@router.get("")
async def get_all_profiles(profile_repository: ProfileRepoDep) -> list[ProfileOutSchema]:
    """
    The base endpoint `/profiles` returns all profiles.

    :param profile_repository: Depends(ProfileRepository)
    :return: all profiles
    """
    logger.info("Fetching all profiles")
    profiles = await profile_repository.get_all()
    return [ProfileOutSchema.model_validate(profile) for profile in profiles]


@router.get("/{profile_id}")
async def get_profile(profile_id: int, profile_repository: ProfileRepoDep) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}` endpoint returns a single profile by id.

    :param profile_id: id of the profile to return
    :param profile_repository: Depends(ProfileRepository)
    :return: the profile, or 404 if it does not exist
    """
    logger.info(f"Fetching profile id={profile_id}")
    profile = await profile_repository.get_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOutSchema.model_validate(profile)


@router.post("", status_code=201)
async def create_profile(payload: ProfileCreateSchema, profile_repository: ProfileRepoDep) -> ProfileOutSchema:
    """
    The `/profiles` POST endpoint creates a new profile. If username is not
    provided, one is auto-generated from the user id.

    :param payload: ProfileCreateSchema - data of the new profile
    :param profile_repository: Depends(ProfileRepository)
    :return: the created profile
    """
    data = payload.model_dump()
    if not data["username"]:
        data["username"] = f"user_{data['user_id']}"
    logger.info(f"Creating profile user_id={payload.user_id} username={data['username']!r}")
    profile = await profile_repository.create(**data)
    return ProfileOutSchema.model_validate(profile)


@router.put("/{profile_id}")
async def update_profile(
    profile_id: int, payload: ProfileUpdateSchema, profile_repository: ProfileRepoDep
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}` PUT endpoint updates an existing profile.

    :param profile_id: id of the profile to update
    :param payload: ProfileUpdateSchema - fields to update
    :param profile_repository: Depends(ProfileRepository)
    :return: the updated profile, or 404 if it does not exist
    """
    logger.info(f"Updating profile id={profile_id}")
    profile = await profile_repository.update_by_id(profile_id, **payload.model_dump(exclude_unset=True))
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOutSchema.model_validate(profile)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(profile_id: int, profile_repository: ProfileRepoDep) -> None:
    """
    The `/profiles/{profile_id}` DELETE endpoint deletes a profile by id.

    :param profile_id: id of the profile to delete
    :param profile_repository: Depends(ProfileRepository)
    :return: None
    """
    logger.info(f"Deleting profile id={profile_id}")
    profile = await profile_repository.delete_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")

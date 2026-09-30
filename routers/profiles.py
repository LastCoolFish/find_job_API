from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.ProfileRepository import ProfileRepository
from repositories.SkillRepository import SkillRepository
from schemas.profile import ProfileCreateSchema, ProfileOutSchema, ProfileUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])

ProfileRepoDep = Annotated[ProfileRepository, Depends()]
SkillRepoDep = Annotated[SkillRepository, Depends()]


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


@router.get("/by-user/{user_id}")
async def get_profile_by_user_id(user_id: int, profile_repository: ProfileRepoDep) -> ProfileOutSchema:
    """
    The `/profiles/by-user/{user_id}` endpoint returns a single profile by user id.

    :param user_id: id of the user whose profile to return
    :param profile_repository: Depends(ProfileRepository)
    :return: the profile, or 404 if it does not exist
    """
    logger.info(f"Fetching profile user_id={user_id}")
    profile = await profile_repository.get_by_user_id(user_id)
    if profile is None:
        logger.warning(f"Profile user_id={user_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOutSchema.model_validate(profile)


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
    created = await profile_repository.create(**data)
    profile = await profile_repository.get_by_id(created.id)
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
    updated = await profile_repository.update_by_id(profile_id, **payload.model_dump(exclude_unset=True))
    if updated is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.post("/{profile_id}/skills/{skill_id}")
async def add_profile_skill(
    profile_id: int,
    skill_id: int,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills/{skill_id}` POST endpoint attaches a skill to a profile.
    Attaching a skill that is already attached is a no-op.

    :param profile_id: id of the profile to attach the skill to
    :param skill_id: id of the skill to attach
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or skill does not exist
    """
    profile = await profile_repository.get_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    skill = await skill_repository.get_by_id(skill_id)
    if skill is None:
        logger.warning(f"Skill id={skill_id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")

    logger.info(f"Attaching skill_id={skill_id} to profile_id={profile_id}")
    await profile_repository.add_skill(profile_id, skill_id)
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.delete("/{profile_id}/skills/{skill_id}")
async def remove_profile_skill(
    profile_id: int,
    skill_id: int,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills/{skill_id}` DELETE endpoint detaches a skill from a profile.
    Detaching a skill that is not attached is a no-op.

    :param profile_id: id of the profile to detach the skill from
    :param skill_id: id of the skill to detach
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or skill does not exist
    """
    profile = await profile_repository.get_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    skill = await skill_repository.get_by_id(skill_id)
    if skill is None:
        logger.warning(f"Skill id={skill_id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")

    logger.info(f"Detaching skill_id={skill_id} from profile_id={profile_id}")
    await profile_repository.remove_skill(profile_id, skill_id)
    profile = await profile_repository.get_by_id(profile_id)
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
        raise HTTPException(status_code=404, detail="Profile not found")

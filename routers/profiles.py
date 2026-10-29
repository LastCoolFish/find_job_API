from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from db.models.ProfileModel import ProfileModel
from dependencies import get_owned_profile
from logging_config import get_logger
from repositories.ProfileRepository import ProfileRepository
from repositories.SkillRepository import SkillRepository
from schemas.profile import ProfileOutSchema, ProfileSkillIdsSchema, ProfileUpdateSchema
from schemas.skill import SkillOutSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/profiles", tags=["profiles"])

ProfileRepoDep = Annotated[ProfileRepository, Depends()]
SkillRepoDep = Annotated[SkillRepository, Depends()]


async def _get_profile_or_404(profile_id: int, profile_repository: ProfileRepository) -> ProfileModel:
    profile = await profile_repository.get_by_id(profile_id)
    if profile is None:
        logger.warning(f"Profile id={profile_id} not found")
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


async def _ensure_skills_exist(skill_ids: list[int], skill_repository: SkillRepository) -> None:
    found = {skill.id for skill in await skill_repository.get_by_ids(skill_ids)}
    missing = sorted(set(skill_ids) - found)
    if missing:
        logger.warning(f"Skills not found: {missing}")
        raise HTTPException(status_code=404, detail=f"Skills not found: {missing}")


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


@router.put("/{profile_id}", dependencies=[Depends(get_owned_profile)])
async def update_profile(
    profile_id: int, payload: ProfileUpdateSchema, profile_repository: ProfileRepoDep
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}` PUT endpoint updates an existing profile.

    Access: only the owner of the profile.

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


@router.get("/{profile_id}/skills", dependencies=[Depends(get_owned_profile)])
async def get_profile_skills(profile_id: int, profile_repository: ProfileRepoDep) -> list[SkillOutSchema]:
    """
    The `/profiles/{profile_id}/skills` GET endpoint returns all skills attached to a profile.

    Access: only the owner of the profile.

    :param profile_id: id of the profile whose skills to return
    :param profile_repository: Depends(ProfileRepository)
    :return: the profile's skills, or 404 if the profile does not exist
    """
    logger.info(f"Fetching skills of profile_id={profile_id}")
    profile = await _get_profile_or_404(profile_id, profile_repository)
    return [SkillOutSchema.model_validate(skill) for skill in profile.skills]


@router.post("/{profile_id}/skills/{skill_id}", dependencies=[Depends(get_owned_profile)])
async def add_profile_skill(
    profile_id: int,
    skill_id: int,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills/{skill_id}` POST endpoint attaches a skill to a profile.
    Attaching a skill that is already attached is a no-op.

    Access: only the owner of the profile.

    :param profile_id: id of the profile to attach the skill to
    :param skill_id: id of the skill to attach
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or skill does not exist
    """
    await _get_profile_or_404(profile_id, profile_repository)
    await _ensure_skills_exist([skill_id], skill_repository)

    logger.info(f"Attaching skill_id={skill_id} to profile_id={profile_id}")
    await profile_repository.add_skills(profile_id, [skill_id])
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.post("/{profile_id}/skills", dependencies=[Depends(get_owned_profile)])
async def add_profile_skills(
    profile_id: int,
    payload: ProfileSkillIdsSchema,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills` POST endpoint attaches several skills to a profile at once.
    Already attached skills are skipped; the rest of the profile's skills stay as they are.

    Access: only the owner of the profile.

    :param profile_id: id of the profile to attach the skills to
    :param payload: ProfileSkillIdsSchema - ids of the skills to attach
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or any of the skills does not exist
    """
    skill_ids = list(dict.fromkeys(payload.skill_ids))
    await _get_profile_or_404(profile_id, profile_repository)
    await _ensure_skills_exist(skill_ids, skill_repository)

    logger.info(f"Attaching skill_ids={skill_ids} to profile_id={profile_id}")
    await profile_repository.add_skills(profile_id, skill_ids)
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.put("/{profile_id}/skills", dependencies=[Depends(get_owned_profile)])
async def set_profile_skills(
    profile_id: int,
    payload: ProfileSkillIdsSchema,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills` PUT endpoint replaces the whole skill set of a profile
    with the given one. An empty list removes all skills.

    Access: only the owner of the profile.

    :param profile_id: id of the profile whose skills to replace
    :param payload: ProfileSkillIdsSchema - ids of the skills the profile must end up with
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or any of the skills does not exist
    """
    skill_ids = list(dict.fromkeys(payload.skill_ids))
    await _get_profile_or_404(profile_id, profile_repository)
    await _ensure_skills_exist(skill_ids, skill_repository)

    logger.info(f"Replacing skills of profile_id={profile_id} with skill_ids={skill_ids}")
    await profile_repository.set_skills(profile_id, skill_ids)
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.delete("/{profile_id}/skills/{skill_id}", dependencies=[Depends(get_owned_profile)])
async def remove_profile_skill(
    profile_id: int,
    skill_id: int,
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills/{skill_id}` DELETE endpoint detaches a skill from a profile.
    Detaching a skill that is not attached is a no-op.

    Access: only the owner of the profile.

    :param profile_id: id of the profile to detach the skill from
    :param skill_id: id of the skill to detach
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or skill does not exist
    """
    await _get_profile_or_404(profile_id, profile_repository)
    await _ensure_skills_exist([skill_id], skill_repository)

    logger.info(f"Detaching skill_id={skill_id} from profile_id={profile_id}")
    await profile_repository.remove_skills(profile_id, [skill_id])
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)


@router.delete("/{profile_id}/skills", dependencies=[Depends(get_owned_profile)])
async def remove_profile_skills(
    profile_id: int,
    skill_ids: Annotated[list[int], Query()],
    profile_repository: ProfileRepoDep,
    skill_repository: SkillRepoDep,
) -> ProfileOutSchema:
    """
    The `/profiles/{profile_id}/skills?skill_ids=1&skill_ids=2` DELETE endpoint detaches several
    skills from a profile at once. Skills that are not attached are skipped.

    Access: only the owner of the profile.

    :param profile_id: id of the profile to detach the skills from
    :param skill_ids: ids of the skills to detach (query parameter, repeat it per id)
    :param profile_repository: Depends(ProfileRepository)
    :param skill_repository: Depends(SkillRepository)
    :return: the updated profile, or 404 if the profile or any of the skills does not exist
    """
    skill_ids = list(dict.fromkeys(skill_ids))
    await _get_profile_or_404(profile_id, profile_repository)
    await _ensure_skills_exist(skill_ids, skill_repository)

    logger.info(f"Detaching skill_ids={skill_ids} from profile_id={profile_id}")
    await profile_repository.remove_skills(profile_id, skill_ids)
    profile = await profile_repository.get_by_id(profile_id)
    return ProfileOutSchema.model_validate(profile)

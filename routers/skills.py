from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.SkillRepository import SkillRepository
from schemas.skill import SkillCreateSchema, SkillOutSchema, SkillUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/skills", tags=["skills"])

SkillRepoDep = Annotated[SkillRepository, Depends()]


@router.get("")
async def get_all_skills(skill_repository: SkillRepoDep) -> list[SkillOutSchema]:
    """
    The base endpoint `/skills` returns all skills.

    :param skill_repository: Depends(SkillRepository)
    :return: all skills
    """
    logger.info("Fetching all skills")
    skills = await skill_repository.get_all()
    return [SkillOutSchema.model_validate(skill) for skill in skills]


@router.get("/{skill_id}")
async def get_skill(skill_id: int, skill_repository: SkillRepoDep) -> SkillOutSchema:
    """
    The `/skills/{skill_id}` endpoint returns a single skill by id.

    :param skill_id: id of the skill to return
    :param skill_repository: Depends(SkillRepository)
    :return: the skill, or 404 if it does not exist
    """
    logger.info(f"Fetching skill id={skill_id}")
    skill = await skill_repository.get_by_id(skill_id)
    if skill is None:
        logger.warning(f"Skill id={skill_id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillOutSchema.model_validate(skill)


@router.post("", status_code=201)
async def create_skill(payload: SkillCreateSchema, skill_repository: SkillRepoDep) -> SkillOutSchema:
    """
    The `/skills` POST endpoint creates a new skill.

    :param payload: SkillCreateSchema - data of the new skill
    :param skill_repository: Depends(SkillRepository)
    :return: the created skill
    """
    logger.info(f"Creating skill name={payload.name!r}")
    skill = await skill_repository.create(**payload.model_dump())
    return SkillOutSchema.model_validate(skill)


@router.put("/{skill_id}")
async def update_skill(skill_id: int, payload: SkillUpdateSchema, skill_repository: SkillRepoDep) -> SkillOutSchema:
    """
    The `/skills/{skill_id}` PUT endpoint updates an existing skill.

    :param skill_id: id of the skill to update
    :param payload: SkillUpdateSchema - fields to update
    :param skill_repository: Depends(SkillRepository)
    :return: the updated skill, or 404 if it does not exist
    """
    logger.info(f"Updating skill id={skill_id}")
    skill = await skill_repository.update_by_id(skill_id, **payload.model_dump(exclude_unset=True))
    if skill is None:
        logger.warning(f"Skill id={skill_id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillOutSchema.model_validate(skill)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: int, skill_repository: SkillRepoDep) -> None:
    """
    The `/skills/{skill_id}` DELETE endpoint deletes a skill by id.

    :param skill_id: id of the skill to delete
    :param skill_repository: Depends(SkillRepository)
    :return: None
    """
    logger.info(f"Deleting skill id={skill_id}")
    skill = await skill_repository.delete_by_id(skill_id)
    if skill is None:
        logger.warning(f"Skill id={skill_id} not found")
        raise HTTPException(status_code=404, detail="Skill not found")


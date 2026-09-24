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
    skills = await skill_repository.get_all()
    return [SkillOutSchema.model_validate(skill) for skill in skills]


@router.get("/{skill_id}")
async def get_skill(skill_id: int, skill_repository: SkillRepoDep) -> SkillOutSchema:
    skill = await skill_repository.get_by_id(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillOutSchema.model_validate(skill)


@router.post("", status_code=201)
async def create_skill(payload: SkillCreateSchema, skill_repository: SkillRepoDep) -> SkillOutSchema:
    skill = await skill_repository.create(**payload.model_dump())
    return SkillOutSchema.model_validate(skill)


@router.put("/{skill_id}")
async def update_skill(skill_id: int, payload: SkillUpdateSchema, skill_repository: SkillRepoDep) -> SkillOutSchema:
    skill = await skill_repository.update_by_id(skill_id, **payload.model_dump(exclude_unset=True))
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillOutSchema.model_validate(skill)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: int, skill_repository: SkillRepoDep) -> None:
    skill = await skill_repository.delete_by_id(skill_id)


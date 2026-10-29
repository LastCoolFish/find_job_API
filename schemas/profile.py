from pydantic import BaseModel

from schemas.skill import SkillOutSchema


class ProfileOutSchema(BaseModel):
    id: int
    user_id: int
    name: str | None
    username: str
    desired_salary: int | None
    desired_format: str | None
    desired_grade: int | None
    skills: list[SkillOutSchema]

    model_config = {"from_attributes": True}


class ProfileUpdateSchema(BaseModel):
    name: str | None = None
    username: str | None = None
    desired_salary: int | None = None
    desired_format: str | None = None
    desired_grade: int | None = None


class ProfileSkillIdsSchema(BaseModel):
    skill_ids: list[int]

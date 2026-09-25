from pydantic import BaseModel, Field

from schemas.skill import SkillOutSchema


class CompanyVacancyCountSchema(BaseModel):
    name: str
    vacancy_count: int


class SkillDemandSchema(BaseModel):
    skill: SkillOutSchema = Field(validation_alias="SkillModel")
    vacancy_count: int

    model_config = {"from_attributes": True}

from pydantic import BaseModel, Field

from schemas.skill import SkillOutSchema
from schemas.vacancy import CompanyBriefSchema


class CompanyVacancyCountSchema(BaseModel):
    company: CompanyBriefSchema = Field(validation_alias="CompanyModel")
    vacancy_count: int

    model_config = {"from_attributes": True}


class SkillDemandSchema(BaseModel):
    skill: SkillOutSchema = Field(validation_alias="SkillModel")
    vacancy_count: int

    model_config = {"from_attributes": True}


class EngagementAnalyticsSchema(BaseModel):
    avg_view_duration: float | None
    link_clicks: int
    total_views: int
    ctr: float

from pydantic import BaseModel, Field, computed_field

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

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def ctr(self) -> float:
        return self.link_clicks / self.total_views if self.total_views else 0.0

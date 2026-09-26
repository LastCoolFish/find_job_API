from pydantic import BaseModel

from schemas.skill import SkillOutSchema


class CompanyBriefSchema(BaseModel):
    id: int
    name: str
    rating: int | None
    accreditation: bool

    model_config = {"from_attributes": True}


class VacancyOutSchema(BaseModel):
    id: int
    job_title: str
    salary: int | None
    description: str
    place: str | None
    grade: int | None
    format: str | None
    platform: str
    platform_id: int
    site_href: str
    company: CompanyBriefSchema
    skills: list[SkillOutSchema]

    model_config = {"from_attributes": True}


class VacancyCreateSchema(BaseModel):
    job_title: str
    salary: int | None = None
    description: str
    place: str | None = None
    grade: int | None = None
    format: str | None = None
    platform: str
    platform_id: int
    site_href: str
    company_id: int


class VacancyUpdateSchema(BaseModel):
    job_title: str | None = None
    salary: int | None = None
    description: str | None = None
    place: str | None = None
    grade: int | None = None
    format: str | None = None
    platform: str | None = None
    platform_id: int | None = None
    site_href: str | None = None
    company_id: int | None = None

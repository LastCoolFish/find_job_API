from pydantic import BaseModel

from schemas.skill import SkillOut


class CompanyBrief(BaseModel):
    id: int
    name: str
    rating: int | None
    accreditation: bool

    model_config = {"from_attributes": True}


class VacancyOut(BaseModel):
    id: int
    job_title: str
    salary: int | None
    description: str
    place: str | None
    grade: int | None
    format: str | None
    platform: str
    company: CompanyBrief
    skills: list[SkillOut]

    model_config = {"from_attributes": True}

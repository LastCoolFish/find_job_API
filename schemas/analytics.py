from pydantic import BaseModel


class CompanyVacancyCount(BaseModel):
    name: str
    vacancy_count: int


class SkillDemand(BaseModel):
    name: str
    vacancy_count: int

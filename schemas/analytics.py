from pydantic import BaseModel


class CompanyVacancyCountSchema(BaseModel):
    name: str
    vacancy_count: int


class SkillDemandSchema(BaseModel):
    name: str
    vacancy_count: int

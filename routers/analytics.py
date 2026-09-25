from typing import Annotated

from fastapi import APIRouter, Depends, Query

from logging_config import get_logger
from repositories.AnalyticsRepository import AnalyticsRepository
from schemas.analytics import CompanyVacancyCountSchema, SkillDemandSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

AnalyticsRepoDep = Annotated[AnalyticsRepository, Depends()]


@router.get("/top-skills")
async def get_top_skills(
    analytics_repository: AnalyticsRepoDep, count: Annotated[int, Query()] = 5
) -> list[SkillDemandSchema]:
    """
    The `/analytics/top-skills` endpoint returns the most in-demand skills across vacancies.

    :param analytics_repository: Depends(AnalyticsRepository)
    :param count: positive - top N skills, negative - bottom N, 0 - the full ranked list
    :return: skills ranked by the number of vacancies requiring them
    """
    logger.info(f"Fetching top skills count={count}")
    rows = await analytics_repository.get_top_skills(count)
    return [SkillDemandSchema.model_validate(row) for row in rows]


@router.get("/top-companies")
async def get_top_companies(
    analytics_repository: AnalyticsRepoDep, count: Annotated[int, Query()] = 5
) -> list[CompanyVacancyCountSchema]:
    """
    The `/analytics/top-companies` endpoint returns the companies posting the most vacancies.

    :param analytics_repository: Depends(AnalyticsRepository)
    :param count: positive - top N companies, negative - bottom N, 0 - the full ranked list
    :return: companies ranked by the number of vacancies they posted
    """
    logger.info(f"Fetching top companies count={count}")
    rows = await analytics_repository.get_top_vacancy_posters(count)
    return [CompanyVacancyCountSchema.model_validate(row) for row in rows]

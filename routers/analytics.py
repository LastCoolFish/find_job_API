from typing import Annotated

from fastapi import APIRouter, Depends, Query

from db.models.EventModel import EventTarget
from logging_config import get_logger
from repositories.AnalyticsRepository import AnalyticsRepository
from repositories.EventRepository import EventRepository
from schemas.analytics import CompanyVacancyCountSchema, EngagementAnalyticsSchema, SkillDemandSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

AnalyticsRepoDep = Annotated[AnalyticsRepository, Depends()]
EventRepoDep = Annotated[EventRepository, Depends()]




@router.get("/top-skills")
async def get_top_skills(
        analytics_repository: AnalyticsRepoDep,
        count: Annotated[int, Query()] = 5
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
        analytics_repository: AnalyticsRepoDep,
        count: Annotated[int, Query()] = 5
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


@router.get("/vacancies/{vacancy_id}")
async def get_vacancy_analytics(vacancy_id: int, event_repository: EventRepoDep) -> EngagementAnalyticsSchema:
    """
    The `/analytics/vacancies/{vacancy_id}` endpoint returns engagement analytics
    for a single vacancy: average view duration, link clicks, total views and CTR.

    :param vacancy_id: id of the vacancy to compute analytics for
    :param event_repository: Depends(EventRepository)
    :return: engagement analytics for the vacancy
    """
    logger.info(f"Fetching vacancy analytics vacancy_id={vacancy_id}")
    data = await event_repository.get_analytic_info(EventTarget.VACANCY, vacancy_id)
    return EngagementAnalyticsSchema.model_validate(data)


@router.get("/orders/{order_id}")
async def get_order_analytics(order_id: int, event_repository: EventRepoDep) -> EngagementAnalyticsSchema:
    """
    The `/analytics/orders/{order_id}` endpoint returns engagement analytics
    for a single order: average view duration, link clicks, total views and CTR.

    :param order_id: id of the order to compute analytics for
    :param event_repository: Depends(EventRepository)
    :return: engagement analytics for the order
    """
    logger.info(f"Fetching order analytics order_id={order_id}")
    data = await event_repository.get_analytic_info(EventTarget.ORDER, order_id)
    return EngagementAnalyticsSchema.model_validate(data)

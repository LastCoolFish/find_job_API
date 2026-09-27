from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from logging_config import get_logger
from repositories.VacancyRepository import VacancyRepository
from schemas.common import SortOrder
from schemas.vacancy import (
    VacancyCreateSchema,
    VacancyFilterSchema,
    VacancyOutSchema,
    VacancySortField,
    VacancyUpdateSchema,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

VacancyRepoDep = Annotated[VacancyRepository, Depends()]


@router.get("")
async def get_all_vacancies(
        vacancy_repository: VacancyRepoDep,
        limit: Annotated[int | None, Query(ge=1, le=100)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        sort_by: VacancySortField | None = None,
        order: SortOrder = "asc",
) -> list[VacancyOutSchema]:
    """
    The base endpoint `/vacancies` returns all vacancies.

    :param vacancy_repository: Depends(VacancyRepository)
    :param limit: max number of vacancies to return, or None for no limit
    :param offset: number of vacancies to skip
    :param sort_by: column to sort by, or None to leave the result unsorted
    :param order: "asc" or "desc"
    :return: all vacancies
    """
    logger.info(f"Fetching all vacancies limit={limit} offset={offset} sort_by={sort_by} order={order}")
    vacancies = await vacancy_repository.get_all(limit=limit, offset=offset, sort_by=sort_by, order=order)
    return [VacancyOutSchema.model_validate(vacancy) for vacancy in vacancies]


@router.get("/by-skills")
async def get_vacancies_by_skills(
        skills_id: Annotated[list[int], Query()],
        vacancy_repository: VacancyRepoDep) -> list[VacancyOutSchema]:
    """
    The `/vacancies/by-skills` endpoint returns vacancies that have all of the given skills.

    :param skills_id: list of skill ids a vacancy must have every one of
    :param vacancy_repository: Depends(VacancyRepository)
    :return: vacancies matching every requested skill
    """
    logger.info(f"Fetching vacancies matching skills_id={skills_id}")
    vacancies = await vacancy_repository.get_by_skills(skills_id)
    return [VacancyOutSchema.model_validate(vacancy) for vacancy in vacancies]


@router.get("/search")
async def search_vacancies(
        vacancy_repository: VacancyRepoDep,
        job_title: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        place: str | None = None,
        grade: int | None = None,
        format: str | None = None,
        platform: str | None = None,
        company_id: int | None = None,
        limit: Annotated[int | None, Query(ge=1, le=100)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        sort_by: VacancySortField | None = None,
        order: SortOrder = "asc",
) -> list[VacancyOutSchema]:
    """
    The `/vacancies/search` endpoint returns vacancies matching every given filter.
    Filters left unset are ignored.

    :param vacancy_repository: Depends(VacancyRepository)
    :param job_title: substring to match against job_title (case-insensitive)
    :param salary_min: minimum salary (inclusive)
    :param salary_max: maximum salary (inclusive)
    :param place: substring to match against place (case-insensitive)
    :param grade: exact grade to match
    :param format: exact format to match
    :param platform: exact platform to match
    :param company_id: exact company id to match
    :param limit: max number of vacancies to return, or None for no limit
    :param offset: number of matching vacancies to skip
    :param sort_by: column to sort by, or None to leave the result unsorted
    :param order: "asc" or "desc"
    :return: vacancies matching all provided filters
    """
    filters = VacancyFilterSchema(
        job_title=job_title,
        salary_min=salary_min,
        salary_max=salary_max,
        place=place,
        grade=grade,
        format=format,
        platform=platform,
        company_id=company_id,
    )
    logger.info(
        f"Searching vacancies filters={filters.model_dump(exclude_none=True)} "
        f"limit={limit} offset={offset} sort_by={sort_by} order={order}"
    )
    vacancies = await vacancy_repository.get_filtered(
        filters, limit=limit, offset=offset, sort_by=sort_by, order=order
    )
    return [VacancyOutSchema.model_validate(vacancy) for vacancy in vacancies]


@router.get("/{vacancy_id}")
async def get_vacancy(vacancy_id: int, vacancy_repository: VacancyRepoDep) -> VacancyOutSchema:
    """
    The `/vacancies/{vacancy_id}` endpoint returns a single vacancy by id.

    :param vacancy_id: id of the vacancy to return
    :param vacancy_repository: Depends(VacancyRepository)
    :return: the vacancy, or 404 if it does not exist
    """
    logger.info(f"Fetching vacancy id={vacancy_id}")
    vacancy = await vacancy_repository.get_by_id(vacancy_id)
    if vacancy is None:
        logger.warning(f"Vacancy id={vacancy_id} not found")
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return VacancyOutSchema.model_validate(vacancy)


@router.post("", status_code=201)
async def create_vacancy(payload: VacancyCreateSchema, vacancy_repository: VacancyRepoDep) -> VacancyOutSchema:
    """
    The `/vacancies` POST endpoint creates a new vacancy.

    :param payload: VacancyCreateSchema - data of the new vacancy
    :param vacancy_repository: Depends(VacancyRepository)
    :return: the created vacancy
    """
    logger.info(f"Creating vacancy job_title={payload.job_title!r}")
    created = await vacancy_repository.create(**payload.model_dump())
    vacancy = await vacancy_repository.get_by_id(created.id)
    return VacancyOutSchema.model_validate(vacancy)


@router.put("/{vacancy_id}")
async def update_vacancy(
        vacancy_id: int, payload: VacancyUpdateSchema, vacancy_repository: VacancyRepoDep
) -> VacancyOutSchema:
    """
    The `/vacancies/{vacancy_id}` PUT endpoint updates an existing vacancy.

    :param vacancy_id: id of the vacancy to update
    :param payload: VacancyUpdateSchema - fields to update
    :param vacancy_repository: Depends(VacancyRepository)
    :return: the updated vacancy, or 404 if it does not exist
    """
    logger.info(f"Updating vacancy id={vacancy_id}")
    updated = await vacancy_repository.update_by_id(vacancy_id, **payload.model_dump(exclude_unset=True))
    if updated is None:
        logger.warning(f"Vacancy id={vacancy_id} not found")
        raise HTTPException(status_code=404, detail="Vacancy not found")
    vacancy = await vacancy_repository.get_by_id(vacancy_id)
    return VacancyOutSchema.model_validate(vacancy)


@router.delete("/{vacancy_id}", status_code=204)
async def delete_vacancy(vacancy_id: int, vacancy_repository: VacancyRepoDep) -> None:
    """
    The `/vacancies/{vacancy_id}` DELETE endpoint deletes a vacancy by id.

    :param vacancy_id: id of the vacancy to delete
    :param vacancy_repository: Depends(VacancyRepository)
    :return: None
    """
    logger.info(f"Deleting vacancy id={vacancy_id}")
    vacancy = await vacancy_repository.delete_by_id(vacancy_id)
    if vacancy is None:
        logger.warning(f"Vacancy id={vacancy_id} not found")
        raise HTTPException(status_code=404, detail="Vacancy not found")

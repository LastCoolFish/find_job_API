from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from logging_config import get_logger
from repositories.VacancyRepository import VacancyRepository
from schemas.vacancy import VacancyCreateSchema, VacancyOutSchema, VacancyUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

VacancyRepoDep = Annotated[VacancyRepository, Depends()]


@router.get("")
async def get_all_vacancies(vacancy_repository: VacancyRepoDep) -> list[VacancyOutSchema]:
    """
    The base endpoint `/vacancies` returns all vacancies.

    :param vacancy_repository: Depends(VacancyRepository)
    :return: all vacancies
    """
    logger.info("Fetching all vacancies")
    vacancies = await vacancy_repository.get_all()
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

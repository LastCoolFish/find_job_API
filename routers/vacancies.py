from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.VacancyRepository import VacancyRepository
from schemas.vacancy import VacancyCreateSchema, VacancyOutSchema, VacancyUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

VacancyRepoDep = Annotated[VacancyRepository, Depends()]


@router.get("")
async def get_all_vacancies(vacancy_repository: VacancyRepoDep) -> list[VacancyOutSchema]:
    vacancies = await vacancy_repository.get_all()
    return [VacancyOutSchema.model_validate(vacancy) for vacancy in vacancies]


@router.get("/{vacancy_id}")
async def get_vacancy(vacancy_id: int, vacancy_repository: VacancyRepoDep) -> VacancyOutSchema:
    vacancy = await vacancy_repository.get_by_id(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return VacancyOutSchema.model_validate(vacancy)


@router.post("", status_code=201)
async def create_vacancy(payload: VacancyCreateSchema, vacancy_repository: VacancyRepoDep) -> VacancyOutSchema:
    created = await vacancy_repository.create(**payload.model_dump())
    vacancy = await vacancy_repository.get_by_id(created.id)
    return VacancyOutSchema.model_validate(vacancy)


@router.put("/{vacancy_id}")
async def update_vacancy(
    vacancy_id: int, payload: VacancyUpdateSchema, vacancy_repository: VacancyRepoDep
) -> VacancyOutSchema:
    updated = await vacancy_repository.update_by_id(vacancy_id, **payload.model_dump(exclude_unset=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    vacancy = await vacancy_repository.get_by_id(vacancy_id)
    return VacancyOutSchema.model_validate(vacancy)


@router.delete("/{vacancy_id}", status_code=204)
async def delete_vacancy(vacancy_id: int, vacancy_repository: VacancyRepoDep) -> None:
    vacancy = await vacancy_repository.delete_by_id(vacancy_id)

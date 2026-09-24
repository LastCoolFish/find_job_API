from typing import TypeVar, Generic, Type

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import request

tModel = TypeVar("tModel")


class BaseRepository(Generic[tModel]):
    model: Type[tModel]

    @request
    async def get_all(self, session: AsyncSession) -> list[tModel]:
        '''
        Returns all records from the selected model's table. \n
        It is a common function for all repositories.

        :param session: sqlalchemy.AsyncSession
        :return: list of models type (tModel)
        '''
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> tModel | None:
        '''
        Returns the model by id, or None if the id does not exist. \n
        It is a common function for all repositories.

        :param model_id: id of the model to return
        :param session: sqlalchemy.AsyncSession
        :return: model type (tModel) | None
        '''
        result = await session.execute(select(self.model).where(self.model.id == model_id))
        return result.scalars().one_or_none()

    @request
    async def delete_by_id(self, model_id: int, session: AsyncSession) -> None:
        '''
        Deletes the model by id; returns the deleted model if successful, otherwise returns None. \n
        It is a common function for all repositories.

        :param model_id: id of the model to return
        :param session: sqlalchemy.AsyncSession
        :return: model type (tModel) | None
        '''
        query = delete(self.model).where(self.model.id == model_id)

    @request
    async def create(self, session: AsyncSession, **kwargs) -> tModel:
        '''
        Adds data to the database and returns the new model. \n
        It is a common function for all repositories.

        :param session: sqlalchemy.AsyncSession
        :param kwargs: data of Model
        :return: new model (tModel)
        '''

        new_model = self.model(**kwargs)
        session.add(new_model)
        await session.flush()
        return new_model

    @request
    async def update_by_id(self, model_id: int, session: AsyncSession, **kwargs) -> tModel | None:
        '''
        Updates the model by id with the given data and returns the updated model. \n
        It is a common function for all repositories.

        :param model_id: id of the model to update
        :param session: sqlalchemy.AsyncSession
        :param kwargs: data to update the model with
        :return: model type (tModel) | None
        '''
        query = update(self.model).where(self.model.id == model_id).values(**kwargs).returning(self.model)
        callback = await session.execute(query)
        return callback.scalars().one_or_none()

    @request
    async def create_many(self, session: AsyncSession, data: list[dict]) -> list[tModel]:
        '''
        Adds multiple records to the database and returns the new models. \n
        It is a common function for all repositories.

        :param session: sqlalchemy.AsyncSession
        :param data: list of dicts with data of Model
        :return: list of new models (tModel)
        '''
        new_models = [self.model(**item) for item in data]
        session.add_all(new_models)
        await session.flush()
        return new_models

    @request
    async def update_many(self, session: AsyncSession, data: list[dict]) -> None:
        '''
        Updates multiple models in a single UPDATE statement. \n
        It is a common function for all repositories.

        Every dict in ``data`` must contain the same set of keys: "id" of the model to update
        and the columns to update it with.

        :param session: sqlalchemy.AsyncSession
        :param data: list of dicts, each containing "id" of the model to update and the data to update it with
        :return: None
        '''
        await session.execute(update(self.model), data)

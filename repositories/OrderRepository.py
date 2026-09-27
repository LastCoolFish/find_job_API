from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import request
from db.models.OrderModel import OrderModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository
from schemas.common import SortOrder
from schemas.order import OrderFilterSchema, OrderSortField

logger = get_logger(__name__)

_SORTABLE_COLUMNS = {
    "id": OrderModel.id,
    "name": OrderModel.name,
    "price": OrderModel.price,
    "publication_timestamp": OrderModel.publication_timestamp,
}


class OrderRepository(BaseRepository[OrderModel]):
    model = OrderModel

    @request
    async def get_all(
        self,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        sort_by: OrderSortField | None = None,
        order: SortOrder = "asc",
    ) -> list[OrderModel]:
        query = select(OrderModel).options(selectinload(OrderModel.customer))
        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        result = await session.execute(query)
        return list(result.scalars().all())

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> OrderModel | None:
        result = await session.execute(
            select(OrderModel)
            .where(OrderModel.id == model_id)
            .options(selectinload(OrderModel.customer))
        )
        return result.scalars().one_or_none()

    @request
    async def get_filtered(
        self,
        filters: OrderFilterSchema,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        sort_by: OrderSortField | None = None,
        order: SortOrder = "asc",
    ) -> list[OrderModel]:
        """
        Returns orders matching every given filter; a filter left as None is not applied. \n

        :param filters: OrderFilterSchema - optional filter values
        :param session: sqlalchemy.AsyncSession
        :param limit: max number of orders to return, or None for no limit
        :param offset: number of matching orders to skip
        :param sort_by: column to sort by, or None to leave the result unsorted
        :param order: "asc" or "desc"
        :return: orders matching all provided filters
        """
        query = select(OrderModel).options(selectinload(OrderModel.customer))

        if filters.name is not None:
            query = query.where(OrderModel.name.ilike(f"%{filters.name}%"))
        if filters.price_min is not None:
            query = query.where(OrderModel.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.where(OrderModel.price <= filters.price_max)
        if filters.platform is not None:
            query = query.where(OrderModel.platform == filters.platform)
        if filters.customer_id is not None:
            query = query.where(OrderModel.customer_id == filters.customer_id)

        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        result = await session.execute(query)
        return list(result.scalars().all())

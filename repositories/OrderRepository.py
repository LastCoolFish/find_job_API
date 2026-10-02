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
    ) -> tuple[list[OrderModel], int]:
        query = select(OrderModel).options(selectinload(OrderModel.customer))
        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        items = list((await session.execute(query)).scalars().all())
        total = await self._count(session)
        return items, total

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> OrderModel | None:
        result = await session.execute(
            select(OrderModel)
            .where(OrderModel.id == model_id)
            .options(selectinload(OrderModel.customer))
        )
        return result.scalars().one_or_none()

    @staticmethod
    def _build_conditions(filters: OrderFilterSchema) -> list:
        """
        Translates an OrderFilterSchema into a list of WHERE conditions; a filter
        left as None does not contribute a condition.

        :param filters: OrderFilterSchema - optional filter values
        :return: list of SQLAlchemy conditions, to be applied with .where(*conditions)
        """
        conditions = []
        if filters.name is not None:
            conditions.append(OrderModel.name.ilike(f"%{filters.name}%"))
        if filters.price_min is not None:
            conditions.append(OrderModel.price >= filters.price_min)
        if filters.price_max is not None:
            conditions.append(OrderModel.price <= filters.price_max)
        if filters.platform is not None:
            conditions.append(OrderModel.platform == filters.platform)
        if filters.customer_id is not None:
            conditions.append(OrderModel.customer_id == filters.customer_id)
        return conditions

    @request
    async def get_filtered(
        self,
        filters: OrderFilterSchema,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
        sort_by: OrderSortField | None = None,
        order: SortOrder = "asc",
    ) -> tuple[list[OrderModel], int]:
        """
        Returns orders matching every given filter; a filter left as None is not applied. \n

        :param filters: OrderFilterSchema - optional filter values
        :param session: sqlalchemy.AsyncSession
        :param limit: max number of orders to return, or None for no limit
        :param offset: number of matching orders to skip
        :param sort_by: column to sort by, or None to leave the result unsorted
        :param order: "asc" or "desc"
        :return: tuple of (orders matching all provided filters, total matching count)
        """
        conditions = self._build_conditions(filters)

        query = select(OrderModel).options(selectinload(OrderModel.customer)).where(*conditions)

        query = self._sort(query, _SORTABLE_COLUMNS.get(sort_by), order)
        query = self._paginate(query, limit, offset)

        items = list((await session.execute(query)).scalars().all())
        total = await self._count(session, *conditions)
        return items, total

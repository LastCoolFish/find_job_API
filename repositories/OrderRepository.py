from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.engine import request
from db.models.OrderModel import OrderModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class OrderRepository(BaseRepository[OrderModel]):
    model = OrderModel

    @request
    async def get_all(self, session: AsyncSession) -> list[OrderModel]:
        result = await session.execute(
            select(OrderModel).options(selectinload(OrderModel.customer))
        )
        return list(result.scalars().all())

    @request
    async def get_by_id(self, model_id: int, session: AsyncSession) -> OrderModel | None:
        result = await session.execute(
            select(OrderModel)
            .where(OrderModel.id == model_id)
            .options(selectinload(OrderModel.customer))
        )
        return result.scalars().one_or_none()

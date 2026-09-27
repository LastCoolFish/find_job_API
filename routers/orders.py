from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from logging_config import get_logger
from repositories.OrderRepository import OrderRepository
from schemas.common import SortOrder
from schemas.order import (
    OrderCreateSchema,
    OrderFilterSchema,
    OrderOutSchema,
    OrderSortField,
    OrderUpdateSchema,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

OrderRepoDep = Annotated[OrderRepository, Depends()]


@router.get("")
async def get_all_orders(
        order_repository: OrderRepoDep,
        limit: Annotated[int | None, Query(ge=1, le=100)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        sort_by: OrderSortField | None = None,
        order: SortOrder = "asc",
) -> list[OrderOutSchema]:
    """
    The base endpoint `/orders` returns all orders.

    :param order_repository: Depends(OrderRepository)
    :param limit: max number of orders to return, or None for no limit
    :param offset: number of orders to skip
    :param sort_by: column to sort by, or None to leave the result unsorted
    :param order: "asc" or "desc"
    :return: all orders
    """
    logger.info(f"Fetching all orders limit={limit} offset={offset} sort_by={sort_by} order={order}")
    orders = await order_repository.get_all(limit=limit, offset=offset, sort_by=sort_by, order=order)
    return [OrderOutSchema.model_validate(order) for order in orders]


@router.get("/search")
async def search_orders(
        order_repository: OrderRepoDep,
        name: str | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        platform: str | None = None,
        customer_id: int | None = None,
        limit: Annotated[int | None, Query(ge=1, le=100)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        sort_by: OrderSortField | None = None,
        order: SortOrder = "asc",
) -> list[OrderOutSchema]:
    """
    The `/orders/search` endpoint returns orders matching every given filter.
    Filters left unset are ignored.

    :param order_repository: Depends(OrderRepository)
    :param name: substring to match against name (case-insensitive)
    :param price_min: minimum price (inclusive)
    :param price_max: maximum price (inclusive)
    :param platform: exact platform to match
    :param customer_id: exact customer id to match
    :param limit: max number of orders to return, or None for no limit
    :param offset: number of matching orders to skip
    :param sort_by: column to sort by, or None to leave the result unsorted
    :param order: "asc" or "desc"
    :return: orders matching all provided filters
    """
    filters = OrderFilterSchema(
        name=name,
        price_min=price_min,
        price_max=price_max,
        platform=platform,
        customer_id=customer_id,
    )
    logger.info(
        f"Searching orders filters={filters.model_dump(exclude_none=True)} "
        f"limit={limit} offset={offset} sort_by={sort_by} order={order}"
    )
    orders = await order_repository.get_filtered(
        filters, limit=limit, offset=offset, sort_by=sort_by, order=order
    )
    return [OrderOutSchema.model_validate(order) for order in orders]


@router.get("/{order_id}")
async def get_order(order_id: int, order_repository: OrderRepoDep) -> OrderOutSchema:
    """
    The `/orders/{order_id}` endpoint returns a single order by id.

    :param order_id: id of the order to return
    :param order_repository: Depends(OrderRepository)
    :return: the order, or 404 if it does not exist
    """
    logger.info(f"Fetching order id={order_id}")
    order = await order_repository.get_by_id(order_id)
    if order is None:
        logger.warning(f"Order id={order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOutSchema.model_validate(order)


@router.post("", status_code=201)
async def create_order(payload: OrderCreateSchema, order_repository: OrderRepoDep) -> OrderOutSchema:
    """
    The `/orders` POST endpoint creates a new order.

    :param payload: OrderCreateSchema - data of the new order
    :param order_repository: Depends(OrderRepository)
    :return: the created order
    """
    logger.info(f"Creating order name={payload.name!r}")
    created = await order_repository.create(**payload.model_dump())
    order = await order_repository.get_by_id(created.id)
    return OrderOutSchema.model_validate(order)


@router.put("/{order_id}")
async def update_order(
    order_id: int, payload: OrderUpdateSchema, order_repository: OrderRepoDep
) -> OrderOutSchema:
    """
    The `/orders/{order_id}` PUT endpoint updates an existing order.

    :param order_id: id of the order to update
    :param payload: OrderUpdateSchema - fields to update
    :param order_repository: Depends(OrderRepository)
    :return: the updated order, or 404 if it does not exist
    """
    logger.info(f"Updating order id={order_id}")
    updated = await order_repository.update_by_id(order_id, **payload.model_dump(exclude_unset=True))
    if updated is None:
        logger.warning(f"Order id={order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")
    order = await order_repository.get_by_id(order_id)
    return OrderOutSchema.model_validate(order)


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, order_repository: OrderRepoDep) -> None:
    """
    The `/orders/{order_id}` DELETE endpoint deletes an order by id.

    :param order_id: id of the order to delete
    :param order_repository: Depends(OrderRepository)
    :return: None
    """
    logger.info(f"Deleting order id={order_id}")
    order = await order_repository.delete_by_id(order_id)
    if order is None:
        logger.warning(f"Order id={order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")


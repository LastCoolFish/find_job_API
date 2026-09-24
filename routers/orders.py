from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from logging_config import get_logger
from repositories.OrderRepository import OrderRepository
from schemas.order import OrderCreateSchema, OrderOutSchema, OrderUpdateSchema

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

OrderRepoDep = Annotated[OrderRepository, Depends()]


@router.get("")
async def get_all_orders(order_repository: OrderRepoDep) -> list[OrderOutSchema]:
    orders = await order_repository.get_all()
    return [OrderOutSchema.model_validate(order) for order in orders]


@router.get("/{order_id}")
async def get_order(order_id: int, order_repository: OrderRepoDep) -> OrderOutSchema:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOutSchema.model_validate(order)


@router.post("", status_code=201)
async def create_order(payload: OrderCreateSchema, order_repository: OrderRepoDep) -> OrderOutSchema:
    created = await order_repository.create(**payload.model_dump())
    order = await order_repository.get_by_id(created.id)
    return OrderOutSchema.model_validate(order)


@router.put("/{order_id}")
async def update_order(
    order_id: int, payload: OrderUpdateSchema, order_repository: OrderRepoDep
) -> OrderOutSchema:
    updated = await order_repository.update_by_id(order_id, **payload.model_dump(exclude_unset=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order = await order_repository.get_by_id(order_id)
    return OrderOutSchema.model_validate(order)


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, order_repository: OrderRepoDep) -> None:
    order = await order_repository.delete_by_id(order_id)


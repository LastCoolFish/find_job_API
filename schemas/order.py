from datetime import datetime
from typing import Literal

from pydantic import BaseModel

OrderSortField = Literal["id", "name", "price", "publication_timestamp"]


class CustomerBriefSchema(BaseModel):
    id: int
    name: str
    href: str | None
    platform: str

    model_config = {"from_attributes": True}


class OrderOutSchema(BaseModel):
    id: int
    name: str
    description: str
    price: int | None
    publication_timestamp: datetime
    platform: str
    platform_id: int
    site_href: str
    customer: CustomerBriefSchema

    model_config = {"from_attributes": True}


class OrderCreateSchema(BaseModel):
    name: str
    description: str
    price: int | None = None
    publication_timestamp: datetime
    platform: str
    platform_id: int
    site_href: str
    customer_id: int


class OrderFilterSchema(BaseModel):
    name: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    platform: str | None = None
    customer_id: int | None = None


class OrderUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    publication_timestamp: datetime | None = None
    platform: str | None = None
    platform_id: int | None = None
    site_href: str | None = None
    customer_id: int | None = None

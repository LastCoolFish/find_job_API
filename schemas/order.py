from datetime import datetime

from pydantic import BaseModel


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


class OrderUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    publication_timestamp: datetime | None = None
    platform: str | None = None
    platform_id: int | None = None
    site_href: str | None = None
    customer_id: int | None = None

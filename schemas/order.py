from datetime import datetime

from pydantic import BaseModel


class CustomerBrief(BaseModel):
    id: int
    name: str
    href: str | None
    platform: str

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    name: str
    description: str
    price: int | None
    publication_timestamp: datetime
    platform: str
    customer: CustomerBrief

    model_config = {"from_attributes": True}

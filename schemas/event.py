from datetime import datetime

from pydantic import BaseModel

from db.models.EventModel import EventTypeEnum


class EventCreate(BaseModel):
    user_id: int
    event_type: EventTypeEnum
    vacancy_id: int | None = None
    order_id: int | None = None
    duration_seconds: int | None = None
    payload: dict | None = None


class EventOutSchema(BaseModel):
    id: int
    user_id: int
    event_type: EventTypeEnum
    vacancy_id: int | None
    order_id: int | None
    duration_seconds: int | None
    payload: dict | None
    occurred_at: datetime

    model_config = {"from_attributes": True}

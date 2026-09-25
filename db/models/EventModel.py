from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Enum as PgEnum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime, Integer

from db.models.BaseModel import BaseModel


class EventTypeEnum(str, enum.Enum):
    VIEW_START = "view_start"
    VIEW_END = "view_end"
    LINK_CLICK = "link_click"
    SEARCH = "search"


class EventModel(BaseModel):
    __tablename__ = "events"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        nullable=False,
    )

    event_type: Mapped[EventTypeEnum] = mapped_column(
        PgEnum(EventTypeEnum, name="event_type"),
        index=True,
        nullable=False,
    )

    # Only one of these is set, depending on what the event happened on;
    # both are null for a SEARCH event.
    vacancy_id: Mapped[int | None] = mapped_column(
        ForeignKey("vacancies.id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
        nullable=True,
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
        nullable=True,
    )

    # Populated only for VIEW_END events.
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Event-specific extra data (search query/filters, clicked link, etc.).
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[BaseModel] = relationship("UserModel", back_populates="events")

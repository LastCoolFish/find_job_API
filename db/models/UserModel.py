from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Enum as PgEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from db.models.BaseModels import BaseModel


class RoleEnum(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    BLOCKED = "blocked"


class UserModel(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    role: Mapped[RoleEnum] = mapped_column(
        PgEnum(RoleEnum, name="user_role"),
        nullable=False,
        default=RoleEnum.USER,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    profile: Mapped[BaseModel] = relationship("ProfileModel", back_populates="user", uselist=False)
    events: Mapped[list[BaseModel]] = relationship("EventModel", back_populates="user")

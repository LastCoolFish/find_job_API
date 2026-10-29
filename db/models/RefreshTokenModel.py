from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime

from db.models.BaseModels import BaseModel


class RefreshTokenModel(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        nullable=False,
    )

    # SHA-256 of the token; the token itself is never stored.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    # All tokens issued by rotating one login share a family, so a whole session can be revoked at once.
    family_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)

    # Set when the token is used up (rotated) or revoked. Kept until expiry so reuse can be detected.
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

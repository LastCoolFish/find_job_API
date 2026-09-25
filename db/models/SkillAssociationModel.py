from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.BaseModel import BaseModel


class SkillAssociationModel(BaseModel):
    """Base for pure association tables linking some entity to SkillModel."""

    __abstract__ = True

    # Pure association table - exclude the surrogate id inherited from BaseModel
    # so the composite primary key alone identifies the row, matching ON CONFLICT.
    id = None

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
    )

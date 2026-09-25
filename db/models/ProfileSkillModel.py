from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.models.SkillAssociationModel import SkillAssociationModel


class ProfileSkillModel(SkillAssociationModel):
    __tablename__ = "profiles_skills"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )

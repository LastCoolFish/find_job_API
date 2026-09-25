from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer, SmallInteger

from db.models.BaseModel import BaseModel


class ProfileModel(BaseModel):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # Unique, but not user-supplied by default - auto-generated at creation
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    desired_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    desired_format: Mapped[str | None] = mapped_column(String(75), nullable=True)
    desired_grade: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    user: Mapped[BaseModel] = relationship("UserModel", back_populates="profile")

    skills: Mapped[list[BaseModel]] = relationship(
        "SkillModel",
        secondary="profiles_skills",
    )

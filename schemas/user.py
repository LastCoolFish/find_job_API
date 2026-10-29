from datetime import datetime

from pydantic import BaseModel, Field, SecretStr, field_validator

from db.models.UserModel import RoleEnum
from schemas.profile import ProfileOutSchema
from security import ensure_fits_bcrypt


class UserOutSchema(BaseModel):
    id: int
    email: str
    phone: str | None
    role: RoleEnum
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class UserWithProfileOutSchema(UserOutSchema):
    profile: ProfileOutSchema


class UserProfileCreateSchema(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    # If not provided, a username is auto-generated from the new user's id.
    username: str | None = Field(default=None, min_length=1, max_length=50)
    desired_salary: int | None = None
    desired_format: str | None = Field(default=None, max_length=75)
    desired_grade: int | None = None


class UserCreateSchema(BaseModel):
    email: str
    phone: str | None = None
    password: SecretStr = Field(min_length=8)
    profile: UserProfileCreateSchema = Field(default_factory=UserProfileCreateSchema)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: SecretStr) -> SecretStr:
        ensure_fits_bcrypt(value.get_secret_value())
        return value


class UserUpdateSchema(BaseModel):
    email: str | None = None
    phone: str | None = None
    role: RoleEnum | None = None

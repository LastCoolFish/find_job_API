from datetime import datetime

from pydantic import BaseModel

from db.models.UserModel import RoleEnum


class UserOutSchema(BaseModel):
    id: int
    email: str
    phone: str | None
    role: RoleEnum
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class UserCreateSchema(BaseModel):
    email: str
    phone: str | None = None
    role: RoleEnum = RoleEnum.USER


class UserUpdateSchema(BaseModel):
    email: str | None = None
    phone: str | None = None
    role: RoleEnum | None = None

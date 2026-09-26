from pydantic import BaseModel


class ProfileOutSchema(BaseModel):
    id: int
    user_id: int
    name: str | None
    username: str
    desired_salary: int | None
    desired_format: str | None
    desired_grade: int | None

    model_config = {"from_attributes": True}


class ProfileCreateSchema(BaseModel):
    user_id: int
    name: str | None = None
    # If not provided, a username is auto-generated from the user id (see router).
    username: str | None = None
    desired_salary: int | None = None
    desired_format: str | None = None
    desired_grade: int | None = None


class ProfileUpdateSchema(BaseModel):
    name: str | None = None
    username: str | None = None
    desired_salary: int | None = None
    desired_format: str | None = None
    desired_grade: int | None = None

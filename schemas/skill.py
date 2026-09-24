from pydantic import BaseModel


class SkillOutSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SkillCreateSchema(BaseModel):
    name: str


class SkillUpdateSchema(BaseModel):
    name: str | None = None

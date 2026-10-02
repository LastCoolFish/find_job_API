from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

SortOrder = Literal["asc", "desc"]

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int | None = None
    offset: int = 0

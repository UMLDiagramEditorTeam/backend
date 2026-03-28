from typing import Sequence, TypeVar

from pydantic import BaseModel as PydanticBaseModel

from app.models import BaseModel

T = TypeVar('T')


class CommonListFilters(PydanticBaseModel):
    page: int
    limit: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse[Model: BaseModel](PydanticBaseModel):
    data: Sequence[Model]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return (self.total + 1) // self.limit

from typing import Sequence

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, computed_field

from app.models import BaseModel


class CommonListFilters(PydanticBaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse[Model: BaseModel](PydanticBaseModel):
    data: Sequence[Model]
    total: int
    page: int
    limit: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit

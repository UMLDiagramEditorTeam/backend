from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.methods import MethodModel


class ArgumentBase(SQLModel):
    name: str = Field(max_length=100)
    type: str = Field(max_length=100)
    order_num: int = Field(ge=0)
    default_value: str | None = Field(default=None)


class ArgumentPublic(BaseModel, ArgumentBase):
    method_id: UUID


class ArgumentCreate(ArgumentBase):
    pass


class ArgumentModel(ArgumentPublic, table=True):
    __tablename__ = 'argument'

    method_id: UUID = Field(foreign_key='method.id')

    method: 'MethodModel' = Relationship(back_populates='arguments')

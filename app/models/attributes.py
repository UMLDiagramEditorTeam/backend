from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.base import AccessModifier, BaseModel

if TYPE_CHECKING:
    from app.models.classes import ClassModel


class AttributeBase(SQLModel):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    type: str = Field(max_length=100)
    is_final: bool = Field(default=False)
    is_static: bool = Field(default=False)
    default_value: str | None = Field(default=None)


class AttributePublic(BaseModel, AttributeBase):
    class_id: UUID = Field(foreign_key='class.id')


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(AttributeBase):
    pass


class AttributeModel(AttributePublic, table=True):
    __tablename__ = 'attribute'

    class_: 'ClassModel' = Relationship(back_populates='attributes')

    __table_args__ = (
        UniqueConstraint('class_id', 'name', name='uq_attribute_class_name'),
    )

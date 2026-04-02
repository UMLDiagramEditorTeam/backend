from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel, UniqueConstraint

from app.models import AccessModifier, BaseModel
from app.models.arguments import ArgumentCreate, ArgumentPublic

if TYPE_CHECKING:
    from app.models import ArgumentModel, ClassModel, InterfaceModel


class MethodBase(SQLModel):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    return_type: str = Field(max_length=100)
    is_final: bool = Field(default=False)
    is_static: bool = Field(default=False)
    is_abstract: bool = Field(default=False)


class MethodPublic(BaseModel, MethodBase):
    class_id: UUID | None = Field(default=None)
    interface_id: UUID | None = Field(default=None)
    arguments: list['ArgumentPublic'] = Field(default=[])


class MethodCreate(MethodBase):
    arguments: list['ArgumentCreate'] = Field(default=[])


class MethodUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    return_type: str | None = Field(default=None, max_length=100)
    is_final: bool | None = Field(default=None)
    is_static: bool | None = Field(default=None)
    is_abstract: bool | None = Field(default=None)
    arguments: list['ArgumentCreate'] = Field(default=[])


class MethodModel(BaseModel, MethodBase, table=True):
    __tablename__ = 'method'

    class_id: UUID | None = Field(default=None, foreign_key='class.id')
    interface_id: UUID | None = Field(default=None, foreign_key='interface.id')

    class_: 'ClassModel' = Relationship(back_populates='methods')
    interface: 'InterfaceModel' = Relationship(back_populates='methods')
    arguments: list['ArgumentModel'] = Relationship(
        back_populates='method',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    __table_args__ = (
        CheckConstraint(
            '(class_id IS NOT NULL AND interface_id IS NULL) '
            'OR (class_id IS NULL AND interface_id IS NOT NULL)',
            name='method_single_parent_check',
        ),
        UniqueConstraint('class_id', 'name', name='uq_method_class_name'),
        UniqueConstraint('interface_id', 'name', name='uq_method_interface_name'),
    )

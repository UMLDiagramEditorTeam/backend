from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel, UniqueConstraint

from app.models.arguments import ArgumentCreate, ArgumentPublic
from app.models.base import BaseModel
from app.models.classes import AccessModifier

if TYPE_CHECKING:
    from app.models import ArgumentModel, ClassModel, InterfaceModel


class MethodBase(SQLModel):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    return_type: str = Field(max_length=100)
    is_final: bool = Field(default=False)
    is_static: bool = Field(default=False)
    is_abstract: bool = Field(default=False)
    is_inherited: bool = Field(default=False)


class MethodPublic(BaseModel, MethodBase):
    class_id: UUID | None = Field(default=None)
    interface_id: UUID | None = Field(default=None)
    arguments: list['ArgumentPublic'] = Field(default=[])


class MethodCreate(MethodBase):
    arguments: list['ArgumentCreate'] = Field(default=[])


class MethodUpdate(MethodBase):
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
        # Логические конфликты
        CheckConstraint(
            'NOT (is_final = TRUE AND is_abstract = TRUE)',
            name='final_abstract_conflict',
        ),
        CheckConstraint(
            'NOT (is_static = TRUE AND is_abstract = TRUE)',
            name='static_abstract_conflict',
        ),
        # Ограничения для интерфейсов
        CheckConstraint(
            """
            (interface_id IS NULL) OR (
            interface_id IS NOT NULL AND
            (access_modifier = 'PUBLIC' OR access_modifier IS NULL)
            AND is_final = FALSE
            AND is_static = FALSE
            )
            """,
            name='interface_method_constraints',
        ),
        # Ограничения для абстрактных методов в классах
        CheckConstraint(
            """
            (class_id IS NULL OR is_abstract = FALSE) OR (
            class_id IS NOT NULL AND is_abstract = TRUE
            AND access_modifier IN ('PUBLIC', 'PROTECTED', NULL)
            )
            """,
            name='abstract_class_method_rules',
        ),
    )

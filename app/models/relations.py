from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models import ClassModel, InterfaceModel, WindowModel


class RelationKind(str, Enum):
    RELATION = 'relation'
    REALIZATION = 'realization'


class RelationEndType(str, Enum):
    RELATION = 'relation'
    ONE = 'one'
    MANY = 'many'
    ONE_ONLY_ONE = 'one_only_one'
    ONE_OR_MANY = 'one_or_many'
    ZERO_OR_ONE = 'zero_or_one'
    ZERO_OR_MANY = 'zero_or_many'


class RelationBase(SQLModel):
    name: str = Field(max_length=100)
    type: RelationKind = Field(default=RelationKind.RELATION)

    begin_type: RelationEndType = Field(default=RelationEndType.RELATION)
    end_type: RelationEndType = Field(default=RelationEndType.RELATION)

    begin_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    begin_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')
    end_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    end_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')


class RelationPublic(BaseModel, RelationBase):
    window_id: UUID | None = Field(foreign_key='window.id')


class RelationCreate(RelationBase):
    pass


class RelationUpdate(RelationBase):
    pass


class RelationModel(RelationPublic, table=True):
    __tablename__ = 'relation'

    begin_class: 'ClassModel' = Relationship(
        back_populates='relations_start',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.begin_class_id'},
    )
    begin_interface: 'InterfaceModel' = Relationship(
        back_populates='relation_start',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.begin_interface_id'},
    )
    end_class: 'ClassModel' = Relationship(
        back_populates='relations_end',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.end_class_id'},
    )
    end_interface: 'InterfaceModel' = Relationship(
        back_populates='relation_end',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.end_interface_id'},
    )
    window: 'WindowModel' = Relationship(back_populates='relations')

    __table_args__ = (
        CheckConstraint(
            (
                '(begin_class_id IS NOT NULL AND begin_interface_id IS NULL) '
                'OR (begin_class_id IS NULL AND begin_interface_id IS NOT NULL)'
            ),
            name='single_begin_entity_check',
        ),
        CheckConstraint(
            (
                '(end_class_id IS NOT NULL AND end_interface_id IS NULL) '
                'OR (end_class_id IS NULL AND end_interface_id IS NOT NULL)'
            ),
            name='single_end_entity_check',
        ),
        UniqueConstraint(
            'window_id',
            'begin_class_id',
            'begin_interface_id',
            'end_class_id',
            'end_interface_id',
            name='uq_relation_unique_pair',
        ),
    )

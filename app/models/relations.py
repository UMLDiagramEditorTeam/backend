from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import CheckConstraint, Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.enums import RelationType

if TYPE_CHECKING:
    from app.models.classes import ClassModel
    from app.models.interfaces import InterfaceModel
    from app.models.windows import WindowModel


class RelationBase(SQLModel):
    name: str = Field(max_length=100)
    start_type: RelationType = Field(default=RelationType.RELATION)
    end_type: RelationType = Field(default=RelationType.RELATION)
    start_class_id: UUID | None
    start_interface_id: UUID | None
    end_class_id: UUID | None
    end_interface_id: UUID | None


class RelationPublic(BaseModel, RelationBase):
    window_id: UUID


class RelationCreate(RelationBase):
    pass


class RelationUpdate(SQLModel):
    start_type: RelationType | None = Field(default=None)
    end_type: RelationType | None = Field(default=None)
    start_id: UUID | None = Field(default=None)
    end_id: UUID | None = Field(default=None)


class RelationModel(RelationPublic, table=True):
    __tablename__ = 'relation'

    start_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    start_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')
    end_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    end_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')
    window_id: UUID | None = Field(foreign_key='window.id')

    start_class: 'ClassModel' = Relationship(
        back_populates='relations_start',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.start_class_id'},
    )
    start_interface: 'InterfaceModel' = Relationship(
        back_populates='relation_start',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.start_interface_id'},
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
                '(start_class_id IS NOT NULL AND start_interface_id IS NULL) '
                'OR (start_class_id IS NULL AND start_interface_id IS NOT NULL)'
            ),
            name='single_start_entity_check',
        ),
        CheckConstraint(
            (
                '(end_class_id IS NOT NULL AND end_interface_id IS NULL) '
                'OR (end_class_id IS NULL AND end_interface_id IS NOT NULL)'
            ),
            name='single_end_entity_check',
        ),
    )

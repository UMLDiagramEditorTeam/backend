from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models import AccessModifier, BaseModel
from app.models.tiles import TileCreate, TileModel, TilePublic, TileUpdate

if TYPE_CHECKING:
    from app.models import AttributeModel, MethodModel, RelationModel, WindowModel


class ClassBase(SQLModel):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    is_abstract: bool = Field(default=False)


class ClassPublic(BaseModel, ClassBase):
    window_id: UUID
    tile: TilePublic


class ClassCreate(ClassBase):
    tile: TileCreate | None = None


class ClassUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    is_abstract: bool | None = Field(default=None)
    tile: TileUpdate | None = None


class ClassModel(BaseModel, ClassBase, table=True):
    __tablename__ = 'class'

    tile_id: UUID | None = Field(default=None, foreign_key='tile.id')
    window_id: UUID = Field(foreign_key='window.id')

    window: 'WindowModel' = Relationship(back_populates='classes')
    tile: 'TileModel' = Relationship(
        back_populates='classes',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
    attributes: list['AttributeModel'] = Relationship(back_populates='class_')
    methods: list['MethodModel'] = Relationship(back_populates='class_')
    relations_start: list['RelationModel'] = Relationship(
        back_populates='start_class',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.start_class_id'},
    )
    relations_end: list['RelationModel'] = Relationship(
        back_populates='end_class',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.end_class_id'},
    )

    __table_args__ = (
        UniqueConstraint('window_id', 'name', name='uq_class_window_name'),
    )

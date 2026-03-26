from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.enums import AccessModifier

if TYPE_CHECKING:
    from app.models.attributes import AttributeModel
    from app.models.methods import MethodModel
    from app.models.relations import RelationModel
    from app.models.tiles import TileCreate, TileModel, TileUpdate
    from app.models.windows import WindowModel


class ClassBase(SQLModel):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    is_abstract: bool = Field(default=False)


class ClassPublic(BaseModel, ClassBase):
    tile_id: UUID | None
    window_id: UUID


class ClassCreate(ClassBase):
    tile: TileCreate | None


class ClassUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    access_modifier: AccessModifier | None = Field(default=None)
    is_abstract: bool | None = Field(default=None)
    tile: TileUpdate | None


class ClassModel(ClassPublic, table=True):
    __tablename__ = 'class'

    tile_id: UUID | None = Field(default=None, foreign_key='tile.id')
    window_id: UUID = Field(foreign_key='window.id')

    window: 'WindowModel' = Relationship(back_populates='window')
    tile: 'TileModel' = Relationship(back_populates='classes')
    attributes: list['AttributeModel'] = Relationship(back_populates='class_')
    methods: list['MethodModel'] = Relationship(back_populates='class_')
    relations_start: list['RelationModel'] = Relationship(back_populates='start_class')
    relations_end: list['RelationModel'] = Relationship(back_populates='end_class')

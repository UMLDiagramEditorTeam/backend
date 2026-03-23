from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.methods import MethodModel
    from app.models.relations import RelationModel
    from app.models.tiles import TileModel


class InterfaceBase(SQLModel):
    name: str = Field(max_length=100)


class InterfacePublic(BaseModel, InterfaceBase):
    tile_id: UUID


class InterfaceCreate(InterfaceBase):
    tile_id: UUID


class InterfaceUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    tile_id: UUID | None = Field(default=None)


class InterfaceModel(InterfacePublic, table=True):
    __tablename__ = 'interface'

    tile_id: UUID = Field(foreign_key='tile.id')

    tile: 'TileModel' = Relationship(back_populates='interfaces')
    methods: list['MethodModel'] = Relationship(back_populates='interface')
    relation_start: list['RelationModel'] = Relationship(
        back_populates='start_interface'
    )
    relation_end: list['RelationModel'] = Relationship(back_populates='end_interface')

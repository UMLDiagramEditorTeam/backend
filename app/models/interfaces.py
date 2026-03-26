from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.methods import MethodModel
    from app.models.relations import RelationModel
    from app.models.tiles import TileCreate, TileModel, TileUpdate
    from app.models.windows import WindowModel


class InterfaceBase(SQLModel):
    name: str = Field(max_length=100)


class InterfacePublic(BaseModel, InterfaceBase):
    tile_id: UUID | None
    window_id: UUID


class InterfaceCreate(InterfaceBase):
    tile: TileCreate | None


class InterfaceUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    tile: TileUpdate | None


class InterfaceModel(InterfacePublic, table=True):
    __tablename__ = 'interface'

    tile_id: UUID = Field(foreign_key='tile.id')
    window_id: UUID = Field(foreign_key='window.id')

    window: 'WindowModel' = Relationship(back_populates='window')
    tile: 'TileModel' = Relationship(back_populates='interfaces')
    methods: list['MethodModel'] = Relationship(back_populates='interface')
    relation_start: list['RelationModel'] = Relationship(
        back_populates='start_interface'
    )
    relation_end: list['RelationModel'] = Relationship(back_populates='end_interface')

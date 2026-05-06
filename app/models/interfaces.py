from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models import BaseModel
from app.models.tiles import TileCreate, TileModel, TilePublic, TileUpdate

if TYPE_CHECKING:
    from app.models import MethodModel, RelationModel, WindowModel


class InterfaceBase(SQLModel):
    name: str = Field(max_length=100)


class InterfacePublic(BaseModel, InterfaceBase):
    window_id: UUID
    tile: TilePublic


class InterfaceCreate(InterfaceBase):
    tile: TileCreate | None = None


class InterfaceUpdate(InterfaceBase):
    tile: TileUpdate


class InterfaceModel(BaseModel, InterfaceBase, table=True):
    __tablename__ = 'interface'

    tile_id: UUID = Field(foreign_key='tile.id')
    window_id: UUID = Field(foreign_key='window.id')

    window: 'WindowModel' = Relationship(back_populates='interfaces')
    tile: 'TileModel' = Relationship(
        back_populates='interfaces',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
    methods: list['MethodModel'] = Relationship(back_populates='interface')
    relation_start: list['RelationModel'] = Relationship(
        back_populates='begin_interface',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.begin_interface_id'},
    )
    relation_end: list['RelationModel'] = Relationship(
        back_populates='end_interface',
        sa_relationship_kwargs={'foreign_keys': 'RelationModel.end_interface_id'},
    )

    __table_args__ = (
        UniqueConstraint('window_id', 'name', name='uq_interface_window_name'),
    )

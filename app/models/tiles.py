from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models import WindowModel
    from app.models.classes import ClassModel
    from app.models.interfaces import InterfaceModel


class TileBase(SQLModel):
    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    width: int = Field(default=200, gt=0)
    height: int = Field(default=150, gt=0)


class TilePublic(BaseModel, TileBase):
    window_id: UUID


class TileCreate(TileBase):
    pass


class TileUpdate(SQLModel):
    x: int | None = Field(default=None, ge=0)
    y: int | None = Field(default=None, ge=0)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)


class TileModel(TilePublic, table=True):
    __tablename__ = 'tile'

    window_id: UUID = Field(foreign_key='window.id')

    window: 'WindowModel' = Relationship(back_populates='tiles')
    classes: list['ClassModel'] = Relationship(back_populates='tile')
    interfaces: list['InterfaceModel'] = Relationship(back_populates='tile')

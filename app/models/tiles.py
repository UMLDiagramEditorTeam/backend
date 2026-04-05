from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models import ClassModel, InterfaceModel


class TileBase(SQLModel):
    x: int = Field(default=0, ge=0)
    y: int = Field(default=0, ge=0)
    width: int = Field(default=200, gt=0)
    height: int = Field(default=150, gt=0)


class TilePublic(BaseModel, TileBase):
    pass


class TileCreate(TileBase):
    pass


class TileUpdate(TileBase):
    pass


class TileModel(TilePublic, table=True):
    __tablename__ = 'tile'

    classes: list['ClassModel'] = Relationship(back_populates='tile')
    interfaces: list['InterfaceModel'] = Relationship(back_populates='tile')

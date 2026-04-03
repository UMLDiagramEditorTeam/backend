from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models import ClassModel, InterfaceModel, ProjectModel, RelationModel


class WindowBase(SQLModel):
    name: str = Field(max_length=200)


class WindowPublic(BaseModel, WindowBase):
    project_id: UUID = Field(foreign_key='project.id')


class WindowCreate(WindowBase):
    pass


class WindowUpdate(WindowBase):
    pass


class WindowModel(WindowPublic, table=True):
    __tablename__ = 'window'

    classes: list['ClassModel'] = Relationship(back_populates='window')
    interfaces: list['InterfaceModel'] = Relationship(back_populates='window')
    project: 'ProjectModel' = Relationship(back_populates='windows')
    relations: list['RelationModel'] = Relationship(back_populates='window')

    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uq_window_project_name'),
    )

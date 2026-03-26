from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.enums import DiagramType

if TYPE_CHECKING:
    from app.models.classes import ClassModel
    from app.models.interfaces import InterfaceModel
    from app.models.projects import ProjectModel
    from app.models.users import UserModel


class WindowBase(SQLModel):
    name: str = Field(max_length=200)
    type: DiagramType = Field(default=DiagramType.CLASS_DIAGRAM)


class WindowPublic(BaseModel, WindowBase):
    project_id: UUID
    user_id: UUID | None = None


class WindowCreate(WindowBase):
    pass


class WindowUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=200)
    type: DiagramType | None = Field(default=None)


class WindowModel(WindowPublic, table=True):
    __tablename__ = 'window'

    project_id: UUID = Field(foreign_key='project.id')
    user_id: UUID | None = Field(default=None, foreign_key='user.id')

    classes: list[ClassModel] = Relationship(back_populates='window')
    interfaces: list[InterfaceModel] = Relationship(back_populates='window')
    project: 'ProjectModel' = Relationship(back_populates='windows')
    user: 'UserModel' = Relationship(back_populates='windows')

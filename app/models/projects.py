from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.windows import WindowModel


class ProjectBase(SQLModel):
    name: str = Field(max_length=200)
    description: str | None = Field(default=None)
    is_imported: bool = Field(default=False)


class ProjectPublic(BaseModel, ProjectBase):
    user_id: UUID


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None)
    is_imported: bool | None = Field(default=None)


class ProjectModel(ProjectPublic, table=True):
    __tablename__ = 'project'

    user_id: UUID = Field(foreign_key='user.id')

    user: 'UserModel' = Relationship(back_populates='projects')
    windows: list['WindowModel'] = Relationship(back_populates='project')

    __table_args__ = (UniqueConstraint('user_id', 'name', name='uq_project_user_name'),)

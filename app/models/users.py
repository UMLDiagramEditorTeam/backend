from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.projects import ProjectModel
    from app.models.windows import WindowModel


class UserBase(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)


class UserPublic(BaseModel, UserBase):
    pass


class UserCreate(UserBase):
    password: str = Field(max_length=50, min_length=6)


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, max_length=50, min_length=6)


class UserModel(UserPublic, table=True):
    __tablename__ = 'user'

    password_hash: str = Field(max_length=100)

    projects: list['ProjectModel'] = Relationship(back_populates='user')
    windows: list['WindowModel'] = Relationship(back_populates='user')

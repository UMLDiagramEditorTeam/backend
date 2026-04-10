from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.user_roles import UserRoleLink

if TYPE_CHECKING:
    from app.models.projects import ProjectModel
    from app.models.refresh_sessions import RefreshSessionModel
    from app.models.roles import RoleModel


class UserBase(SQLModel):
    name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100, unique=True, index=True)


class UserPublic(BaseModel, UserBase):
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(max_length=50, min_length=6)


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, max_length=50, min_length=6)
    is_active: bool | None = None


class UserModel(UserPublic, table=True):
    __tablename__ = 'user'

    password_hash: str = Field(max_length=255)
    is_active: bool = Field(default=True, nullable=False)

    projects: list['ProjectModel'] = Relationship(back_populates='user')
    roles: list['RoleModel'] = Relationship(
        back_populates='users',
        link_model=UserRoleLink,
    )
    refresh_sessions: list['RefreshSessionModel'] = Relationship(
        back_populates='user',
    )

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.role_permissions import RolePermissionLink
from app.models.user_roles import UserRoleLink

if TYPE_CHECKING:
    from app.models.permissions import PermissionModel
    from app.models.users import UserModel


class RoleBase(SQLModel):
    name: str = Field(max_length=100, unique=True, index=True)
    description: str | None = Field(default=None, max_length=255)


class RolePublic(BaseModel, RoleBase):
    pass


class RoleModel(RolePublic, table=True):
    __tablename__ = 'role'

    users: list['UserModel'] = Relationship(
        back_populates='roles',
        link_model=UserRoleLink,
    )
    permissions: list['PermissionModel'] = Relationship(
        back_populates='roles',
        link_model=RolePermissionLink,
    )

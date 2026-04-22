from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.models.role_permissions import RolePermissionLink

if TYPE_CHECKING:
    from app.models.roles import RoleModel


class PermissionBase(SQLModel):
    subject: str = Field(max_length=100)
    action: str = Field(max_length=100)
    scope: str = Field(max_length=200, unique=True, index=True)


class PermissionPublic(BaseModel, PermissionBase):
    pass


class PermissionModel(PermissionPublic, table=True):
    __tablename__ = 'permission'

    roles: list['RoleModel'] = Relationship(
        back_populates='permissions',
        link_model=RolePermissionLink,
    )

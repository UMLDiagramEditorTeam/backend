from collections.abc import Iterable

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.models.user_roles import UserRoleLink
from app.models.users import UserModel

ROLE_SCOPES_MAP: dict[str, list[str]] = {
    'public': [
        'users:me',
        'projects:list_own',
        'projects:read_own',
        'projects:create',
        'projects:update_own',
        'projects:delete_own',
        'windows:list_own',
        'windows:read_own',
        'windows:create_own',
        'windows:update_own',
        'windows:delete_own',
        'classes:list_own',
        'classes:read_own',
        'classes:create_own',
        'classes:update_own',
        'classes:delete_own',
        'interfaces:list_own',
        'interfaces:read_own',
        'interfaces:create_own',
        'interfaces:update_own',
        'interfaces:delete_own',
        'methods:list_own',
        'methods:read_own',
        'methods:create_own',
        'methods:update_own',
        'methods:delete_own',
        'attributes:list_own',
        'attributes:read_own',
        'attributes:create_own',
        'attributes:update_own',
        'attributes:delete_own',
        'relations:list_own',
        'relations:read_own',
        'relations:create_own',
        'relations:update_own',
        'relations:delete_own',
    ],
    'admin': [
        'users:list',
        'users:read',
        'users:create',
        'users:update',
        'users:delete',
        'users:update_roles',
        'users:me',
        'projects:list_own',
        'projects:read_own',
        'projects:create',
        'projects:update_own',
        'projects:delete_own',
        'windows:list_own',
        'windows:read_own',
        'windows:create_own',
        'windows:update_own',
        'windows:delete_own',
        'classes:list_own',
        'classes:read_own',
        'classes:create_own',
        'classes:update_own',
        'classes:delete_own',
        'interfaces:list_own',
        'interfaces:read_own',
        'interfaces:create_own',
        'interfaces:update_own',
        'interfaces:delete_own',
        'methods:list_own',
        'methods:read_own',
        'methods:create_own',
        'methods:update_own',
        'methods:delete_own',
        'attributes:list_own',
        'attributes:read_own',
        'attributes:create_own',
        'attributes:update_own',
        'attributes:delete_own',
        'relations:list_own',
        'relations:read_own',
        'relations:create_own',
        'relations:update_own',
        'relations:delete_own',
    ],
}


class RBACService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_role_by_name(self, name: str) -> RoleModel | None:
        statement = (
            select(RoleModel)
            .where(RoleModel.name == name)
            .options(selectinload(RoleModel.permissions))
        )
        result = await self._session.exec(statement)
        return result.first()

    async def get_permission_by_scope(self, scope: str) -> PermissionModel | None:
        statement = select(PermissionModel).where(PermissionModel.scope == scope)
        result = await self._session.exec(statement)
        return result.first()

    async def get_or_create_permission(self, scope: str) -> PermissionModel:
        permission = await self.get_permission_by_scope(scope)
        if permission is not None:
            return permission

        subject, action = scope.split(':', maxsplit=1)
        permission = PermissionModel(
            subject=subject,
            action=action,
            scope=scope,
        )
        self._session.add(permission)
        await self._session.commit()
        await self._session.refresh(permission)
        return permission

    async def get_or_create_role(
        self,
        name: str,
        description: str | None = None,
    ) -> RoleModel:
        role = await self.get_role_by_name(name)
        if role is not None:
            return role

        role = RoleModel(name=name, description=description)
        self._session.add(role)
        await self._session.commit()
        await self._session.refresh(role)
        return role

    async def assign_role_to_user(self, user: UserModel, role_name: str) -> UserModel:
        role = await self.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Role "{role_name}" not found',
            )

        statement = select(UserRoleLink).where(
            UserRoleLink.user_id == user.id,
            UserRoleLink.role_id == role.id,
        )
        result = await self._session.exec(statement)
        existing_link = result.first()

        if existing_link is None:
            self._session.add(
                UserRoleLink(
                    user_id=user.id,
                    role_id=role.id,
                )
            )
            await self._session.commit()

        loaded_user = await self._session.get(UserModel, user.id)
        if loaded_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found after role assignment',
            )

        return loaded_user

    async def replace_user_roles(
        self,
        user: UserModel,
        role_names: Iterable[str],
    ) -> UserModel:
        roles: list[RoleModel] = []

        for role_name in role_names:
            role = await self.get_role_by_name(role_name)
            if role is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Role "{role_name}" not found',
                )
            roles.append(role)

        await self._session.exec(
            delete(UserRoleLink).where(UserRoleLink.user_id == user.id)
        )

        for role in roles:
            self._session.add(
                UserRoleLink(
                    user_id=user.id,
                    role_id=role.id,
                )
            )

        await self._session.commit()

        loaded_user = await self._session.get(UserModel, user.id)
        if loaded_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found',
            )

        return loaded_user

    @staticmethod
    def collect_user_scopes(user: UserModel) -> set[str]:
        scopes: set[str] = set()
        for role in user.roles:
            if role.name == 'admin':
                return {'*'}
            for permission in role.permissions:
                scopes.add(permission.scope)
        return scopes

from collections.abc import Iterable
from uuid import UUID

from app.core.config import settings
from app.core.errors import NotFoundError
from app.dependencies.repositories import (
    PermissionRepositoryDep,
    RolePermissionRepositoryDep,
    RoleRepositoryDep,
    UserRepositoryDep,
    UserRoleRepositoryDep,
)
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.models.users import UserModel


class RBACService:
    def __init__(
        self,
        role_repository: RoleRepositoryDep,
        permission_repository: PermissionRepositoryDep,
        user_repository: UserRepositoryDep,
        user_role_repository: UserRoleRepositoryDep,
        role_permission_repository: RolePermissionRepositoryDep,
    ):
        self._role_repo = role_repository
        self._permission_repo = permission_repository
        self._user_repo = user_repository
        self._user_role_repo = user_role_repository
        self._role_permission_repo = role_permission_repository

    async def get_role_by_name(self, name: str) -> RoleModel | None:
        roles = await self._role_repo.fetch(name=name, relations=['permissions'])
        return roles[0] if roles else None

    async def get_permission_by_scope(self, scope: str) -> PermissionModel | None:
        permissions = await self._permission_repo.fetch(scope=scope)
        return permissions[0] if permissions else None

    async def get_or_create_permission(self, scope: str) -> PermissionModel:
        permission = await self.get_permission_by_scope(scope)
        if permission:
            return permission

        subject, action = scope.split(':', maxsplit=1)

        return await self._permission_repo.save(
            PermissionModel(
                subject=subject,
                action=action,
                scope=scope,
            )
        )

    async def get_or_create_role(
        self,
        name: str,
        description: str | None = None,
    ) -> RoleModel:
        role = await self.get_role_by_name(name)
        if role:
            return role

        return await self._role_repo.save(RoleModel(name=name, description=description))

    async def assign_role_to_user(self, user: UserModel, role_name: str) -> UserModel:
        role = await self.get_role_by_name(role_name)
        if role is None:
            raise NotFoundError()

        links = await self._user_role_repo.fetch(
            user_id=user.id,
            role_id=role.id,
        )

        if not links:
            await self._user_role_repo.save(
                self._user_role_repo.model(
                    user_id=user.id,
                    role_id=role.id,
                )
            )

        return await self.get_user_with_roles_and_permissions(user.id) or user

    async def replace_user_roles(
        self,
        user: UserModel,
        role_names: Iterable[str],
    ) -> UserModel:
        roles: list[RoleModel] = []

        for role_name in role_names:
            role = await self.get_role_by_name(role_name)
            if role is None:
                raise NotFoundError()
            roles.append(role)

        existing_links = await self._user_role_repo.fetch(user_id=user.id)

        for link in existing_links:
            await self._user_role_repo.delete_instance(link)

        for role in roles:
            await self._user_role_repo.save(
                self._user_role_repo.model(
                    user_id=user.id,
                    role_id=role.id,
                )
            )

        return await self.get_user_with_roles_and_permissions(user.id) or user

    async def get_user_with_roles_and_permissions(
        self,
        user_id: UUID,
    ) -> UserModel | None:
        users = await self._user_repo.fetch(
            id=user_id,
            relations=['roles'],
        )

        user = users[0] if users else None
        if user is None:
            return None

        for role in user.roles:
            await self._role_repo.fetch(id=role.id, relations=['permissions'])

        return user

    def collect_user_scopes(self, user: UserModel) -> set[str]:
        scopes: set[str] = set()

        for role in user.roles:
            if role.name == settings.rbac.admin_role:
                return {'*'}

            for permission in role.permissions:
                scopes.add(permission.scope)

        return scopes

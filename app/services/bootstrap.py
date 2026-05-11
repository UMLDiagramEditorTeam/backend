from app.core.config import settings
from app.core.rbac_map import ROLE_SCOPES_MAP
from app.dependencies.repositories import RoleRepository, UserRepository
from app.models.permissions import PermissionModel
from app.models.users import UserModel, UserStatus
from app.services.hasher import hash_password
from app.services.rbac import RBACService


class BootstrapService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        rbac_service: RBACService,
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._rbac_service = rbac_service

    async def bootstrap_roles_and_permissions(self) -> None:
        all_scopes: set[str] = set()
        for scopes in ROLE_SCOPES_MAP.values():
            all_scopes.update(scopes)

        created_permissions: dict[str, PermissionModel] = {}
        for scope in all_scopes:
            permission = await self._rbac_service.get_or_create_permission(scope)
            created_permissions[scope] = permission

        public_role = await self._rbac_service.get_or_create_role(
            settings.rbac.default_role,
            description='Default role for registered users',
        )
        admin_role = await self._rbac_service.get_or_create_role(
            settings.rbac.admin_role,
            description='Administrator role',
        )

        public_role.permissions.clear()
        public_role.permissions.extend(
            [
                created_permissions[scope]
                for scope in ROLE_SCOPES_MAP.get(settings.rbac.default_role, [])
            ]
        )

        admin_role.permissions.clear()
        admin_role.permissions.extend(list(created_permissions.values()))

        await self._role_repository.save(public_role)
        await self._role_repository.save(admin_role)

    async def bootstrap_admin_user(self) -> None:
        users = await self._user_repository.fetch(email=settings.rbac.admin_email)
        admin_user = users[0] if users else None

        if admin_user is None:
            admin_user = await self._user_repository.save(
                UserModel(
                    name=settings.rbac.admin_name,
                    email=settings.rbac.admin_email,
                    password_hash=hash_password(settings.rbac.admin_password),
                    is_active=True,
                    status=UserStatus.CONFIRMED,
                )
            )
        elif admin_user.status != UserStatus.CONFIRMED:
            admin_user.status = UserStatus.CONFIRMED
            await self._user_repository.save(admin_user)

        await self._rbac_service.assign_role_to_user(
            admin_user,
            settings.rbac.admin_role,
        )

    async def run(self) -> None:
        await self.bootstrap_roles_and_permissions()
        await self.bootstrap_admin_user()

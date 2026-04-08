from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.models.permissions import PermissionModel
from app.models.users import UserModel
from app.services.hasher import hash_password
from app.services.rbac import ROLE_SCOPES_MAP, RBACService


class BootstrapService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._rbac_service = RBACService(session)

    async def bootstrap_roles_and_permissions(self) -> None:
        all_scopes: set[str] = set()
        for scopes in ROLE_SCOPES_MAP.values():
            all_scopes.update(scopes)

        created_permissions: dict[str, PermissionModel] = {}
        for scope in all_scopes:
            permission = await self._rbac_service.get_or_create_permission(scope)
            created_permissions[scope] = permission

        public_role = await self._rbac_service.get_or_create_role(
            settings.rbac_default_role,
            description='Default role for registered users',
        )
        admin_role = await self._rbac_service.get_or_create_role(
            settings.rbac_admin_role,
            description='Administrator role',
        )

        public_role.permissions.clear()
        public_role.permissions.extend(
            [
                created_permissions[scope]
                for scope in ROLE_SCOPES_MAP.get(settings.rbac_default_role, [])
            ]
        )

        admin_role.permissions.clear()
        admin_role.permissions.extend(list(created_permissions.values()))

        self._session.add(public_role)
        self._session.add(admin_role)
        await self._session.commit()

    async def bootstrap_admin_user(self) -> None:
        statement = select(UserModel).where(
            UserModel.email == settings.rbac_admin_email
        )
        result = await self._session.exec(statement)
        admin_user = result.first()

        if admin_user is None:
            admin_user = UserModel(
                name=settings.rbac_admin_name,
                email=settings.rbac_admin_email,
                password_hash=hash_password(settings.rbac_admin_password),
                is_active=True,
            )
            self._session.add(admin_user)
            await self._session.commit()
            await self._session.refresh(admin_user)

        await self._rbac_service.assign_role_to_user(
            admin_user,
            settings.rbac_admin_role,
        )

    async def run(self) -> None:
        await self.bootstrap_roles_and_permissions()
        await self.bootstrap_admin_user()

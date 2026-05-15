import asyncio
from contextlib import asynccontextmanager

from app.db.database import engine
from app.dependencies.repositories import (
    get_permission_repository,
    get_role_permission_repository,
    get_role_repository,
    get_user_repository,
    get_user_role_repository,
)
from app.dependencies.session import get_session
from app.services.bootstrap import BootstrapService
from app.services.rbac import RBACService


async def init_rbac() -> None:
    get_session_context = asynccontextmanager(get_session)
    get_user_repository_context = asynccontextmanager(get_user_repository)
    get_role_repository_context = asynccontextmanager(get_role_repository)
    get_permission_repository_context = asynccontextmanager(get_permission_repository)
    get_user_role_repository_context = asynccontextmanager(get_user_role_repository)
    get_role_permission_repository_context = asynccontextmanager(
        get_role_permission_repository
    )

    async with (
        get_session_context() as session,
        get_user_repository_context(session) as user_repository,
        get_role_repository_context(session) as role_repository,
        get_permission_repository_context(session) as permission_repository,
        get_user_role_repository_context(session) as user_role_repository,
        get_role_permission_repository_context(session) as role_permission_repository,
    ):
        rbac_service = RBACService(
            role_repository=role_repository,
            permission_repository=permission_repository,
            user_repository=user_repository,
            user_role_repository=user_role_repository,
            role_permission_repository=role_permission_repository,
        )

        bootstrap_service = BootstrapService(
            user_repository=user_repository,
            role_repository=role_repository,
            rbac_service=rbac_service,
        )

        await bootstrap_service.run()


async def main() -> None:
    try:
        await init_rbac()
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())

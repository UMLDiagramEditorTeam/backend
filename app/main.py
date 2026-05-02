from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.db.database import async_session_factory
from app.models.permissions import PermissionModel
from app.models.role_permissions import RolePermissionLink
from app.models.roles import RoleModel
from app.models.user_roles import UserRoleLink
from app.models.users import UserModel
from app.routers import (
    attributes,
    auth,
    classes,
    interfaces,
    methods,
    projects,
    relations,
    users,
    windows,
)
from app.services.bootstrap import BootstrapService
from app.services.rbac import RBACService
from app.utils.repository import Repository

api_prefix = '/api'

api_version = 'v1'


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with async_session_factory() as session:
        user_repository = Repository[UserModel](session)
        role_repository = Repository[RoleModel](session)
        permission_repository = Repository[PermissionModel](session)
        user_role_repository = Repository[UserRoleLink](session)
        role_permission_repository = Repository[RolePermissionLink](session)

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

    yield


app = FastAPI(
    title='UML Diagram Editor API',
    version=api_version,
    openapi_url=f'{api_prefix}/openapi.json',
    docs_url=f'{api_prefix}/docs',
    redoc_url=f'{api_prefix}/redoc',
    lifespan=lifespan,
)

app_router = APIRouter(prefix=f'{api_prefix}/{api_version}')

app_router.include_router(auth.router)
app_router.include_router(users.router)
app_router.include_router(projects.router)
app_router.include_router(windows.router)
app_router.include_router(classes.router)
app_router.include_router(interfaces.router)
app_router.include_router(methods.class_methods_router)
app_router.include_router(methods.interface_methods_router)
app_router.include_router(attributes.router)
app_router.include_router(relations.router)

app.include_router(app_router)

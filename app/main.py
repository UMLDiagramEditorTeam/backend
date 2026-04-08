from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.db.database import async_session_factory
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

api_prefix = '/api'


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with async_session_factory() as session:
        bootstrap_service = BootstrapService(session)
        await bootstrap_service.run()
    yield


app = FastAPI(
    title='UML Diagram Editor API',
    version='1.1.1',
    openapi_url=f'{api_prefix}/openapi.json',
    docs_url=f'{api_prefix}/docs',
    redoc_url=f'{api_prefix}/redoc',
    lifespan=lifespan,
)

app_router = APIRouter(prefix=f'{api_prefix}/v1')

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

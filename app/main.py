from fastapi import APIRouter, FastAPI

from app.routers import (
    attributes,
    classes,
    interfaces,
    methods,
    projects,
    relations,
    users,
    windows,
)

api_prefix = '/api'
app = FastAPI(
    title='UML Diagram Editor API',
    version='1.1.1',
    openapi_url=f'{api_prefix}/openapi.json',
    docs_url=f'{api_prefix}/docs',
    redoc_url=f'{api_prefix}/redoc',
)

app_router = APIRouter(prefix=f'{api_prefix}/v1')

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

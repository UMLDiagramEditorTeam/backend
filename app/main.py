from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.error_handlers import exception_handler
from app.core.middlewares import request_logging_middleware
from app.routers import (
    attributes,
    auth,
    classes,
    health,
    interfaces,
    methods,
    projects,
    relations,
    users,
    windows,
)

api_prefix = '/api'

api_version = 'v1'

default_rate_limits = ['100/minute']

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=default_rate_limits,
    headers_enabled=True,
)


app = FastAPI(
    title='UML Diagram Editor API',
    version=api_version,
    openapi_url=f'{api_prefix}/openapi.json' if settings.common.debug else None,
    docs_url=f'{api_prefix}/docs' if settings.common.debug else None,
    redoc_url=f'{api_prefix}/redoc' if settings.common.debug else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(exc_class_or_status_code=Exception, handler=exception_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.common.host],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type', 'X-Requested-With'],
)
app.middleware('http')(request_logging_middleware)

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
app_router.include_router(health.router)

app.include_router(app_router)

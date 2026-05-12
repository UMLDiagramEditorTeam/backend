from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt import PyJWTError

from app.core.responses import (
    auth_responses,
    bad_request_responses,
    common_responses,
    conflict_responses,
    detail_responses,
)
from app.schemas.errors import InternalServerErrorSchema, UnauthorizedErrorSchema
from app.utils.logger import logger


async def exception_handler(
    request: Request,
    exc: Exception,
):
    log_data = {
        'path': request.url.path,
        'method': request.method,
        'client_host': (request.client.host if request.client else None),
    }

    if isinstance(exc, RequestValidationError):
        logger.warning(
            'validation_error',
            **log_data,
        )

        return JSONResponse(
            status_code=422,
            content={
                'message': 'Validation error',
                'detail': exc.errors(),
            },
        )

    if isinstance(exc, PyJWTError):
        logger.warning(
            'jwt_error',
            **log_data,
        )

        return JSONResponse(
            status_code=401,
            content=UnauthorizedErrorSchema().model_dump(),
        )

    status_code = 500

    responses = {
        **common_responses,
        **auth_responses,
        **detail_responses,
        **conflict_responses,
        **bad_request_responses,
    }

    for code, config in responses.items():
        model = config.get('model', InternalServerErrorSchema)()
        error_cls = model.error_cls
        if isinstance(exc, error_cls):
            status_code = code
            break

    return JSONResponse(
        status_code=status_code,
        content={
            'message': getattr(exc, 'message', None),
            'detail': getattr(exc, 'detail', None),
        },
    )

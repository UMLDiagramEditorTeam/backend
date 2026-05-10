import time

from fastapi import Request

from app.utils.logger import logger


async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    log_data = {
        'path': request.url.path,
        'method': request.method,
        'client_host': (request.client.host if request.client else None),
    }

    logger.info(
        'Request started',
        **log_data,
    )

    try:
        response = await call_next(request)

    except Exception:
        logger.error(
            'Unhandled exception encountered',
            **log_data,
        )
        raise

    duration = round(
        time.perf_counter() - start_time,
        4,
    )

    logger.info(
        'Request finished',
        status_code=response.status_code,
        duration=duration,
        **log_data,
    )

    return response

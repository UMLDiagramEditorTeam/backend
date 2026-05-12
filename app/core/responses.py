from app.schemas.errors import (
    BadRequestsSchema,
    ConflictErrorSchema,
    ForbiddenErrorSchema,
    InternalServerErrorSchema,
    NotFoundErrorSchema,
    OkSchema,
    UnauthorizedErrorSchema,
)

ok_responses = {200: {'model': OkSchema}}


bad_request_responses = {
    400: {'model': BadRequestsSchema},
}

unauthorized_responses = {
    401: {'model': UnauthorizedErrorSchema},
}

auth_responses = {
    **unauthorized_responses,
    403: {'model': ForbiddenErrorSchema},
}

detail_responses = {404: {'model': NotFoundErrorSchema}}

conflict_responses = {
    409: {'model': ConflictErrorSchema},
}

common_responses = {500: {'model': InternalServerErrorSchema}}

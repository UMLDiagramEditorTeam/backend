from typing import Optional

from pydantic import Field, PrivateAttr
from sqlmodel import SQLModel

from app.core.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
)


class ErrorSchema(SQLModel):
    details: Optional[dict] = Field(default_factory=dict)
    message: str
    _error: type[Exception] = PrivateAttr(default=Exception)

    @property
    def error(self) -> type[Exception]:
        return self._error


class ValidationErrorItem(SQLModel):
    field: str
    message: str
    code: Optional[str] = None


class BadRequestsSchema(ErrorSchema):
    _error: type[Exception] = BadRequestError


class UnauthorizedErrorSchema(ErrorSchema):
    _error: type[Exception] = UnauthorizedError
    message: str = UnauthorizedError.message


class ForbiddenErrorSchema(ErrorSchema):
    _error: type[Exception] = ForbiddenError
    message: str = ForbiddenError.message


class NotFoundErrorSchema(ErrorSchema):
    _error: type[Exception] = NotFoundError
    message: str = NotFoundError.message


class ConflictErrorSchema(ErrorSchema):
    _error: type[Exception] = ConflictError
    message: str = ConflictError.message


class InternalServerErrorSchema(ErrorSchema):
    _error: type[Exception] = InternalServerError
    message: str = InternalServerError.message


class OkSchema(SQLModel):
    message: str = 'Success'

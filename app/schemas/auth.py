from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.users import UserPublic


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPair(TokenResponse):
    refresh_token: str


class MeResponse(BaseModel):
    user: UserPublic


class SuccessResponse(BaseModel):
    success: bool = True


class AccountConfirmationRequest(BaseModel):
    user_id: UUID
    code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    user_id: UUID
    code: str
    password: str = Field(max_length=50, min_length=6)
    password_confirm: str = Field(max_length=50, min_length=6)

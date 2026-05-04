from pydantic import BaseModel, EmailStr

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

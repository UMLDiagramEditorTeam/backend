from pydantic import BaseModel, EmailStr

from app.models.users import UserPublic


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class MeResponse(BaseModel):
    user: UserPublic


class SuccessResponse(BaseModel):
    success: bool = True

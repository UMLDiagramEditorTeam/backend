from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.roles import RoleModel
from app.models.users import UserCreate, UserModel
from app.services.hasher import hash_password, verify_password
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from app.services.rbac import RBACService
from app.services.refresh_session import RefreshSessionService
from app.services.users import UserService


class AuthService:
    def __init__(
        self,
        session,
        user_service: UserService,
    ):
        self._session = session
        self._user_service = user_service
        self._refresh_session_service = RefreshSessionService(session)
        self._rbac_service = RBACService(session)

    async def register(self, user_create: UserCreate) -> UserModel:
        existing_user = await self._user_service.get_user_by_email(user_create.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with this email already exists',
            )

        user_dump = user_create.model_dump()
        password = str(user_dump.pop('password'))
        password_hash = hash_password(password)

        user = UserModel(
            **user_dump,
            password_hash=password_hash,
            is_active=True,
        )
        user = await self._user_service.create_user_model(user)
        user = await self._rbac_service.assign_role_to_user(
            user,
            settings.rbac_default_role,
        )
        return user

    async def authenticate_user(self, email: str, password: str) -> UserModel:
        user = await self._user_service.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid credentials',
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='User is inactive',
            )
        return user

    async def login(self, email: str, password: str) -> dict:
        user = await self.authenticate_user(email, password)

        access_token, access_jti, _ = create_access_token(user.id)
        refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(user.id)

        await self._refresh_session_service.create_session(
            user_id=user.id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            expires_at=refresh_expires_at,
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user,
        }

    async def get_current_user_by_access_token(self, access_token: str) -> UserModel:
        payload = decode_access_token(access_token)
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token',
            )

        user = await self._user_service.get_user(UUID(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found',
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='User is inactive',
            )
        return user

    async def get_current_user_with_roles(self, access_token: str) -> UserModel:
        user = await self.get_current_user_by_access_token(access_token)
        loaded_user = await self._session.get(
            UserModel,
            user.id,
            options=[selectinload(UserModel.roles).selectinload(RoleModel.permissions)],
        )
        if loaded_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found',
            )
        return loaded_user

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get('sub')
        refresh_jti = payload.get('jti')

        if user_id is None or refresh_jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid refresh token',
            )

        refresh_session = (
            await self._refresh_session_service.get_valid_session_by_refresh_jti(
                refresh_jti
            )
        )
        if refresh_session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Refresh session is invalid',
            )

        user = await self._user_service.get_user(UUID(user_id))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User not found or inactive',
            )

        await self._refresh_session_service.invalidate_session(refresh_session)

        access_token, access_jti, _ = create_access_token(user.id)
        new_refresh_token, new_refresh_jti, refresh_expires_at = create_refresh_token(
            user.id
        )

        await self._refresh_session_service.create_session(
            user_id=user.id,
            access_jti=access_jti,
            refresh_jti=new_refresh_jti,
            expires_at=refresh_expires_at,
        )

        return {
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'user': user,
        }

    async def logout(self, refresh_token: str) -> None:
        payload = decode_refresh_token(refresh_token)
        refresh_jti = payload.get('jti')
        if refresh_jti is None:
            return
        await self._refresh_session_service.invalidate_session_by_refresh_jti(
            refresh_jti
        )

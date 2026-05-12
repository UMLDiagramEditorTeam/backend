from datetime import datetime, timezone
from secrets import token_urlsafe
from uuid import UUID

from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.dependencies.repositories import UserRepositoryDep
from app.dependencies.services import (
    EmailNotificationServiceDep,
    EmailServiceDep,
    RBACServiceDep,
    RefreshSessionServiceDep,
)
from app.models.email_notifications import (
    EmailNotificationAction,
    EmailNotificationCreate,
)
from app.models.refresh_sessions import RefreshSessionCreate
from app.models.users import UserCreate, UserModel, UserStatus
from app.schemas.auth import PasswordChangeRequest, TokenPair
from app.services.hasher import hash_password, verify_password
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepositoryDep,
        refresh_session_service: RefreshSessionServiceDep,
        rbac_service: RBACServiceDep,
        email_notification_service: EmailNotificationServiceDep,
        email_service: EmailServiceDep,
    ):
        self._user_repository = user_repository
        self._refresh_session_service = refresh_session_service
        self._rbac_service = rbac_service
        self._email_notification_service = email_notification_service
        self._email_service = email_service

    async def get_user_by_email(self, email: str) -> UserModel | None:
        users = await self._user_repository.fetch(email=email)
        if len(users) != 1:
            return None
        return users[0]

    async def register(
        self,
        user_create: UserCreate,
        background_tasks: BackgroundTasks,
    ) -> UserModel:
        existing_user = await self.get_user_by_email(user_create.email)
        if existing_user is not None:
            raise ConflictError('Пользователь с таким email уже существует')

        user_dump = user_create.model_dump()
        password = str(user_dump.pop('password'))

        created_user = await self._user_repository.save(
            UserModel(
                **user_dump,
                password_hash=hash_password(password),
                is_active=True,
                status=UserStatus.CREATED,
            )
        )

        created_user = await self._rbac_service.assign_role_to_user(
            created_user,
            settings.rbac.default_role,
        )

        code = await self._create_email_notification(
            user=created_user,
            action=EmailNotificationAction.ACCOUNT_CONFIRMATION,
        )
        self._email_service.send_account_confirmation(
            background_tasks=background_tasks,
            user=created_user,
            code=code,
        )

        return created_user

    async def confirm_account(self, user_id: UUID, code: str) -> UserModel:
        user = await self._user_repository.get(user_id)
        if user is None:
            raise NotFoundError()

        notification = await self._email_notification_service.get_valid_notification(
            user_id=user_id,
            code=code,
            action=EmailNotificationAction.ACCOUNT_CONFIRMATION,
        )

        user.status = UserStatus.CONFIRMED
        await self._user_repository.save(user)
        await self._email_notification_service.mark_as_used(notification)
        return user

    async def authenticate_user(self, email: str, password: str) -> UserModel:
        user = await self.get_user_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError('Неверно введена почта или пароль')

        if not user.is_active:
            raise ForbiddenError('Аккаунт не активен')

        if user.status != UserStatus.CONFIRMED:
            raise ForbiddenError('Аккаунт не подтвержден')

        return user

    async def login(self, email: str, password: str) -> TokenPair:
        user = await self.authenticate_user(email, password)
        return await self._issue_tokens(user)

    async def get_current_user_by_access_token(self, access_token: str) -> UserModel:
        payload = decode_access_token(access_token)
        user_id = payload.get('sub')

        if user_id is None:
            raise UnauthorizedError('Невалидный access-токен')

        user = await self._user_repository.get(UUID(user_id))
        if user is None:
            raise UnauthorizedError('Пользователь не найден')

        if not user.is_active:
            raise ForbiddenError('Аккаунт не активен')

        if user.status != UserStatus.CONFIRMED:
            raise ForbiddenError('Аккаунт не подтвержден')

        return user

    async def get_current_user_with_roles(self, access_token: str) -> UserModel:
        user = await self.get_current_user_by_access_token(access_token)

        loaded_user = await self._rbac_service.get_user_with_roles_and_permissions(
            user.id
        )
        if loaded_user is None:
            raise UnauthorizedError('Пользователь не найден')

        return loaded_user

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get('sub')
        refresh_jti = payload.get('jti')

        if user_id is None or refresh_jti is None:
            raise UnauthorizedError('Невалидный refresh-токен')

        refresh_session = (
            await self._refresh_session_service.get_valid_session_by_refresh_jti(
                refresh_jti
            )
        )
        if refresh_session is None:
            raise UnauthorizedError('Сессия невалидна')

        user = await self._user_repository.get(UUID(user_id))
        if user is None or not user.is_active or user.status != UserStatus.CONFIRMED:
            raise UnauthorizedError('Аккаунт не найден или неактивен')

        await self._refresh_session_service.invalidate_session(refresh_session)

        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        payload = decode_refresh_token(refresh_token)
        refresh_jti = payload.get('jti')

        if refresh_jti is None:
            raise UnauthorizedError('Невалидный refresh-токен')

        await self._refresh_session_service.invalidate_session_by_refresh_jti(
            refresh_jti
        )

    async def request_password_reset(
        self,
        email: str,
        background_tasks: BackgroundTasks,
    ) -> None:
        user = await self.get_user_by_email(email)
        if user is None:
            return

        code = await self._create_email_notification(
            user=user,
            action=EmailNotificationAction.PASSWORD_RESET,
        )
        self._email_service.send_password_reset(
            background_tasks=background_tasks,
            user=user,
            code=code,
        )

    async def change_password(self, request: PasswordChangeRequest) -> None:
        if request.password != request.password_confirm:
            raise BadRequestError('Пароль не совпадает')

        user = await self._user_repository.get(request.user_id)
        if user is None:
            raise UnauthorizedError('Пользователь не найден')

        notification = await self._email_notification_service.get_valid_notification(
            user_id=request.user_id,
            code=request.code,
            action=EmailNotificationAction.PASSWORD_RESET,
        )

        user.password_hash = hash_password(request.password)
        await self._user_repository.save(user)
        await self._email_notification_service.mark_as_used(notification)
        await self._refresh_session_service.invalidate_sessions_by_user_id(user.id)

    async def _issue_tokens(self, user: UserModel) -> TokenPair:
        access_token, access_jti, _ = create_access_token(user.id)
        refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(user.id)

        await self._refresh_session_service.create_session(
            RefreshSessionCreate(
                user_id=user.id,
                access_jti=access_jti,
                refresh_jti=refresh_jti,
                expires_at=refresh_expires_at,
            )
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def _create_email_notification(
        self,
        user: UserModel,
        action: EmailNotificationAction,
    ) -> str:
        expire = (
            settings.auth.account_confirmation_token_expire
            if action == EmailNotificationAction.ACCOUNT_CONFIRMATION
            else settings.auth.password_reset_token_expire
        )
        code = token_urlsafe(32)
        await self._email_notification_service.create_notification(
            EmailNotificationCreate(
                user_id=user.id,
                action=action,
                code=code,
                expired_at=datetime.now(timezone.utc) + expire,
            )
        )
        return code

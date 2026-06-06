import json
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.models  # noqa: F401
from app.db.database import get_session
from app.main import app
from app.models.permissions import PermissionModel
from app.models.role_permissions import RolePermissionLink
from app.models.roles import RoleModel
from app.models.user_roles import UserRoleLink
from app.models.users import UserModel
from app.services.bootstrap import BootstrapService
from app.services.email import EmailService
from app.services.email_notifications import EmailNotificationService
from app.services.rbac import RBACService
from app.services.refresh_session import RefreshSessionService
from app.utils.repository import Repository

API_PREFIX = '/api/v1'
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


class StubEmailService:
    def send_account_confirmation(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def send_password_reset(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class SQLiteEmailNotificationService(EmailNotificationService):
    async def get_valid_notification(self, user_id, code, action):
        notifications = await self._email_notification_repository.fetch(
            user_id=user_id,
            code=code,
            action=action,
            is_used=False,
        )
        notification = notifications[0] if notifications else None

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Email notification not found',
            )

        if as_utc(notification.expired_at) <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email notification is expired',
            )

        return notification


class SQLiteRefreshSessionService(RefreshSessionService):
    async def get_valid_session_by_refresh_jti(self, refresh_jti):
        sessions = await self._refresh_session_repository.fetch(
            refresh_jti=refresh_jti,
            is_valid=True,
        )
        refresh_session = sessions[0] if sessions else None

        if refresh_session is None:
            return None

        if as_utc(refresh_session.expires_at) <= datetime.now(timezone.utc):
            refresh_session.is_valid = False
            await self._refresh_session_repository.save(refresh_session)
            return None

        return refresh_session


def load_fixture(name: str) -> dict[str, Any]:
    with (FIXTURES_DIR / name).open(encoding='utf-8') as fixture_file:
        return json.load(fixture_file)


@pytest.fixture
async def db_session(tmp_path: Path) -> AsyncGenerator[AsyncSession, None]:
    db_path = tmp_path / 'test.db'
    engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}')

    @event.listens_for(engine.sync_engine, 'connect')
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    async with session_factory() as session:
        user_repository = Repository[UserModel](session)
        role_repository = Repository[RoleModel](session)
        permission_repository = Repository[PermissionModel](session)
        user_role_repository = Repository[UserRoleLink](session)
        role_permission_repository = Repository[RolePermissionLink](session)

        rbac_service = RBACService(
            role_repository,
            permission_repository,
            user_repository,
            user_role_repository,
            role_permission_repository,
        )
        bootstrap_service = BootstrapService(
            user_repository,
            role_repository,
            rbac_service,
        )
        await bootstrap_service.bootstrap_roles_and_permissions()
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[EmailService] = StubEmailService
    app.dependency_overrides[EmailNotificationService] = SQLiteEmailNotificationService
    app.dependency_overrides[RefreshSessionService] = SQLiteRefreshSessionService

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://testserver',
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()

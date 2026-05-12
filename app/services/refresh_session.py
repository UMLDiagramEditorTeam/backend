from datetime import datetime, timezone
from uuid import UUID

from app.dependencies.repositories import (
    RefreshSessionRepositoryDep,
)
from app.models.refresh_sessions import RefreshSessionCreate, RefreshSessionModel


class RefreshSessionService:
    def __init__(self, refresh_session_repository: RefreshSessionRepositoryDep):
        self._refresh_session_repository = refresh_session_repository

    async def create_session(
        self,
        refresh_session_create: RefreshSessionCreate,
    ) -> RefreshSessionModel:
        refresh_session = RefreshSessionModel(
            **refresh_session_create.model_dump(),
        )
        return await self._refresh_session_repository.save(refresh_session)

    async def get_valid_session_by_refresh_jti(
        self,
        refresh_jti: str,
    ) -> RefreshSessionModel | None:
        sessions = await self._refresh_session_repository.fetch(
            refresh_jti=refresh_jti,
            is_valid=True,
        )
        refresh_session = sessions[0] if sessions else None

        if refresh_session is None:
            return None

        if refresh_session.expires_at <= datetime.now(timezone.utc):
            refresh_session.is_valid = False
            await self._refresh_session_repository.save(refresh_session)
            return None

        return refresh_session

    async def invalidate_session(self, refresh_session: RefreshSessionModel) -> None:
        refresh_session.is_valid = False
        await self._refresh_session_repository.save(refresh_session)

    async def invalidate_session_by_refresh_jti(self, refresh_jti: str) -> None:
        refresh_session = await self.get_valid_session_by_refresh_jti(refresh_jti)
        if refresh_session is None:
            return

        await self.invalidate_session(refresh_session)

    async def invalidate_sessions_by_user_id(self, user_id: UUID) -> None:
        refresh_sessions = await self._refresh_session_repository.fetch(
            user_id=user_id,
            is_valid=True,
        )
        for refresh_session in refresh_sessions:
            refresh_session.is_valid = False
            await self._refresh_session_repository.save(refresh_session)

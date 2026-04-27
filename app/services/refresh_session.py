from datetime import datetime, timezone
from uuid import UUID

from app.dependencies.repositories import RefreshSessionRepository
from app.models.refresh_sessions import RefreshSessionModel


class RefreshSessionService:
    def __init__(self, refresh_session_repository: RefreshSessionRepository):
        self._refresh_session_repository = refresh_session_repository

    async def create_session(
        self,
        user_id: UUID,
        access_jti: str,
        refresh_jti: str,
        expires_at: datetime,
    ) -> RefreshSessionModel:
        refresh_session = RefreshSessionModel(
            user_id=user_id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            expires_at=expires_at,
            is_valid=True,
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

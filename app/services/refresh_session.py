from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.refresh_sessions import RefreshSessionModel


class RefreshSessionService:
    def __init__(self, session: AsyncSession):
        self._session = session

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
        self._session.add(refresh_session)
        await self._session.commit()
        await self._session.refresh(refresh_session)
        return refresh_session

    async def get_valid_session_by_refresh_jti(
        self,
        refresh_jti: str,
    ) -> RefreshSessionModel | None:
        statement = select(RefreshSessionModel).where(
            RefreshSessionModel.refresh_jti == refresh_jti,
            RefreshSessionModel.is_valid.is_(True),
        )
        result = await self._session.exec(statement)
        refresh_session = result.first()
        if refresh_session is None:
            return None
        if refresh_session.expires_at <= datetime.now(timezone.utc):
            refresh_session.is_valid = False
            self._session.add(refresh_session)
            await self._session.commit()
            return None
        return refresh_session

    async def invalidate_session(self, refresh_session: RefreshSessionModel) -> None:
        refresh_session.is_valid = False
        self._session.add(refresh_session)
        await self._session.commit()

    async def invalidate_session_by_refresh_jti(self, refresh_jti: str) -> None:
        refresh_session = await self.get_valid_session_by_refresh_jti(refresh_jti)
        if refresh_session is None:
            return
        await self.invalidate_session(refresh_session)

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.dependencies.repositories import EmailNotificationRepositoryDep
from app.models.email_notifications import (
    EmailNotificationAction,
    EmailNotificationCreate,
    EmailNotificationModel,
)


class EmailNotificationService:
    def __init__(
        self,
        email_notification_repository: EmailNotificationRepositoryDep,
    ):
        self._email_notification_repository = email_notification_repository

    async def create_notification(
        self,
        notification_create: EmailNotificationCreate,
    ) -> EmailNotificationModel:
        return await self._email_notification_repository.save(
            EmailNotificationModel(**notification_create.model_dump())
        )

    async def get_valid_notification(
        self,
        user_id: UUID,
        code: str,
        action: EmailNotificationAction,
    ) -> EmailNotificationModel:
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

        if notification.expired_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email notification is expired',
            )

        return notification

    async def mark_as_used(
        self,
        notification: EmailNotificationModel,
    ) -> EmailNotificationModel:
        notification.is_used = True
        return await self._email_notification_repository.save(notification)

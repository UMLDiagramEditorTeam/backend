from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.users import UserModel


class EmailNotificationAction(StrEnum):
    ACCOUNT_CONFIRMATION = 'ACCOUNT_CONFIRMATION'
    PASSWORD_RESET = 'PASSWORD_RESET'


class EmailNotificationBase(BaseModel):
    user_id: UUID = Field(foreign_key='user.id', nullable=False, index=True)
    action: EmailNotificationAction = Field(nullable=False, index=True)
    code: str = Field(max_length=64, index=True)
    is_used: bool = Field(default=False, nullable=False)
    expired_at: datetime = Field(
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )


class EmailNotificationModel(EmailNotificationBase, table=True):
    __tablename__ = 'email_notification'

    user: 'UserModel' = Relationship(back_populates='email_notifications')


class EmailNotificationCreate(EmailNotificationBase):
    pass

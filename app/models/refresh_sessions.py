from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.users import UserModel


class RefreshSessionBase(SQLModel):
    user_id: UUID = Field(foreign_key='user.id', nullable=False, index=True)
    access_jti: str = Field(max_length=64, index=True)
    refresh_jti: str = Field(max_length=64, unique=True, index=True)
    expires_at: datetime = Field(
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )
    is_valid: bool = Field(default=True, nullable=False)


class RefreshSessionModel(BaseModel, RefreshSessionBase, table=True):
    __tablename__ = 'refresh_session'

    user: 'UserModel' = Relationship(back_populates='refresh_sessions')

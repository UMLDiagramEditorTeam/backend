from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),  # type: ignore
        sa_column_kwargs={
            'onupdate': lambda: datetime.now(timezone.utc),
        },
    )


class AccessModifier(str, Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'
    DEFAULT = 'default'

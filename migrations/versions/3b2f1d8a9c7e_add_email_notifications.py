"""add email notifications

Revision ID: 3b2f1d8a9c7e
Revises: f11767e98c64
Create Date: 2026-05-08 16:55:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3b2f1d8a9c7e'
down_revision: Union[str, Sequence[str], None] = 'f11767e98c64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

email_notification_action = postgresql.ENUM(
    'ACCOUNT_CONFIRMATION',
    'PASSWORD_RESET',
    name='emailnotificationaction',
    create_type=False,
)
user_status = postgresql.ENUM(
    'CREATED',
    'CONFIRMED',
    name='userstatus',
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    postgresql.ENUM(
        'ACCOUNT_CONFIRMATION',
        'PASSWORD_RESET',
        name='emailnotificationaction',
    ).create(op.get_bind(), checkfirst=True)
    postgresql.ENUM(
        'CREATED',
        'CONFIRMED',
        name='userstatus',
    ).create(op.get_bind(), checkfirst=True)
    op.add_column(
        'user',
        sa.Column(
            'status',
            user_status,
            server_default='CONFIRMED',
            nullable=False,
        ),
    )
    op.alter_column('user', 'status', server_default=None)
    op.create_table(
        'email_notification',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('action', email_notification_action, nullable=False),
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False),
        sa.Column('expired_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_email_notification_action'),
        'email_notification',
        ['action'],
        unique=False,
    )
    op.create_index(
        op.f('ix_email_notification_code'),
        'email_notification',
        ['code'],
        unique=False,
    )
    op.create_index(
        op.f('ix_email_notification_user_id'),
        'email_notification',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_email_notification_user_id'), table_name='email_notification'
    )
    op.drop_index(op.f('ix_email_notification_code'), table_name='email_notification')
    op.drop_index(op.f('ix_email_notification_action'), table_name='email_notification')
    op.drop_table('email_notification')
    op.drop_column('user', 'status')
    user_status.drop(op.get_bind(), checkfirst=True)
    email_notification_action.drop(op.get_bind(), checkfirst=True)

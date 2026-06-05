"""add cascade delete constraints

Revision ID: c4e9f2a1b8d7
Revises: d7720f0836c9
Create Date: 2026-06-05 23:40:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c4e9f2a1b8d7'
down_revision: Union[str, Sequence[str], None] = 'd7720f0836c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('interface', 'tile_id', existing_type=sa.Uuid(), nullable=True)
    op.alter_column('relation', 'window_id', existing_type=sa.Uuid(), nullable=False)

    op.drop_constraint('project_user_id_fkey', 'project', type_='foreignkey')
    op.create_foreign_key(None, 'project', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('window_project_id_fkey', 'window', type_='foreignkey')
    op.create_foreign_key(None, 'window', 'project', ['project_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('class_tile_id_fkey', 'class', type_='foreignkey')
    op.create_foreign_key(None, 'class', 'tile', ['tile_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('class_window_id_fkey', 'class', type_='foreignkey')
    op.create_foreign_key(None, 'class', 'window', ['window_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('interface_tile_id_fkey', 'interface', type_='foreignkey')
    op.create_foreign_key(None, 'interface', 'tile', ['tile_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('interface_window_id_fkey', 'interface', type_='foreignkey')
    op.create_foreign_key(None, 'interface', 'window', ['window_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('attribute_class_id_fkey', 'attribute', type_='foreignkey')
    op.create_foreign_key(None, 'attribute', 'class', ['class_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('method_class_id_fkey', 'method', type_='foreignkey')
    op.create_foreign_key(None, 'method', 'class', ['class_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('method_interface_id_fkey', 'method', type_='foreignkey')
    op.create_foreign_key(None, 'method', 'interface', ['interface_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('relation_window_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'window', ['window_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('relation_begin_class_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'class', ['begin_class_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('relation_begin_interface_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'interface', ['begin_interface_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('relation_end_class_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'class', ['end_class_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('relation_end_interface_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'interface', ['end_interface_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('argument_method_id_fkey', 'argument', type_='foreignkey')
    op.create_foreign_key(None, 'argument', 'method', ['method_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('refresh_session_user_id_fkey', 'refresh_session', type_='foreignkey')
    op.create_foreign_key(None, 'refresh_session', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('email_notification_user_id_fkey', 'email_notification', type_='foreignkey')
    op.create_foreign_key(None, 'email_notification', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('user_role_user_id_fkey', 'user_role', type_='foreignkey')
    op.create_foreign_key(None, 'user_role', 'user', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('user_role_role_id_fkey', 'user_role', type_='foreignkey')
    op.create_foreign_key(None, 'user_role', 'role', ['role_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('role_permission_role_id_fkey', 'role_permission', type_='foreignkey')
    op.create_foreign_key(None, 'role_permission', 'role', ['role_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('role_permission_permission_id_fkey', 'role_permission', type_='foreignkey')
    op.create_foreign_key(None, 'role_permission', 'permission', ['permission_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('argument_method_id_fkey', 'argument', type_='foreignkey')
    op.create_foreign_key(None, 'argument', 'method', ['method_id'], ['id'])

    op.drop_constraint('relation_end_interface_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'interface', ['end_interface_id'], ['id'])

    op.drop_constraint('relation_end_class_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'class', ['end_class_id'], ['id'])

    op.drop_constraint('relation_begin_interface_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'interface', ['begin_interface_id'], ['id'])

    op.drop_constraint('relation_begin_class_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'class', ['begin_class_id'], ['id'])

    op.drop_constraint('relation_window_id_fkey', 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'window', ['window_id'], ['id'])

    op.drop_constraint('method_interface_id_fkey', 'method', type_='foreignkey')
    op.create_foreign_key(None, 'method', 'interface', ['interface_id'], ['id'])

    op.drop_constraint('method_class_id_fkey', 'method', type_='foreignkey')
    op.create_foreign_key(None, 'method', 'class', ['class_id'], ['id'])

    op.drop_constraint('attribute_class_id_fkey', 'attribute', type_='foreignkey')
    op.create_foreign_key(None, 'attribute', 'class', ['class_id'], ['id'])

    op.drop_constraint('interface_window_id_fkey', 'interface', type_='foreignkey')
    op.create_foreign_key(None, 'interface', 'window', ['window_id'], ['id'])

    op.drop_constraint('interface_tile_id_fkey', 'interface', type_='foreignkey')
    op.create_foreign_key(None, 'interface', 'tile', ['tile_id'], ['id'])

    op.drop_constraint('class_window_id_fkey', 'class', type_='foreignkey')
    op.create_foreign_key(None, 'class', 'window', ['window_id'], ['id'])

    op.drop_constraint('class_tile_id_fkey', 'class', type_='foreignkey')
    op.create_foreign_key(None, 'class', 'tile', ['tile_id'], ['id'])

    op.drop_constraint('window_project_id_fkey', 'window', type_='foreignkey')
    op.create_foreign_key(None, 'window', 'project', ['project_id'], ['id'])

    op.drop_constraint('role_permission_permission_id_fkey', 'role_permission', type_='foreignkey')
    op.create_foreign_key(None, 'role_permission', 'permission', ['permission_id'], ['id'])

    op.drop_constraint('role_permission_role_id_fkey', 'role_permission', type_='foreignkey')
    op.create_foreign_key(None, 'role_permission', 'role', ['role_id'], ['id'])

    op.drop_constraint('user_role_role_id_fkey', 'user_role', type_='foreignkey')
    op.create_foreign_key(None, 'user_role', 'role', ['role_id'], ['id'])

    op.drop_constraint('user_role_user_id_fkey', 'user_role', type_='foreignkey')
    op.create_foreign_key(None, 'user_role', 'user', ['user_id'], ['id'])

    op.drop_constraint('email_notification_user_id_fkey', 'email_notification', type_='foreignkey')
    op.create_foreign_key(None, 'email_notification', 'user', ['user_id'], ['id'])

    op.drop_constraint('refresh_session_user_id_fkey', 'refresh_session', type_='foreignkey')
    op.create_foreign_key(None, 'refresh_session', 'user', ['user_id'], ['id'])

    op.drop_constraint('project_user_id_fkey', 'project', type_='foreignkey')
    op.create_foreign_key(None, 'project', 'user', ['user_id'], ['id'])

    op.alter_column('relation', 'window_id', existing_type=sa.Uuid(), nullable=True)
    op.alter_column('interface', 'tile_id', existing_type=sa.Uuid(), nullable=False)

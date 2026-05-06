"""update relations models

Revision ID: f11767e98c64
Revises: 8f15a8f134bc
Create Date: 2026-04-20 17:57:11.442308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f11767e98c64'
down_revision: Union[str, Sequence[str], None] = '8f15a8f134bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


old_type = sa.Enum('RELATION', 'ONE', 'MANY', 'ONE_AND_ONLY_ONE', 'ONE_OR_MANY', 'ZERO_OR_ONE', 'ZERO_OR_MANY',
                   name='relationtype')
new_type = sa.Enum('RELATION', 'ONE', 'MANY', 'ONE_ONLY_ONE', 'ONE_OR_MANY', 'ZERO_OR_ONE', 'ZERO_OR_MANY',
                   name='relationendtype')
relation_kind_type = sa.Enum('RELATION', 'REALIZATION', name='relationkind')

def upgrade() -> None:
    """Upgrade schema."""
    relation_kind_type.create(op.get_bind(), checkfirst=False)
    op.add_column('relation', sa.Column('type', relation_kind_type, nullable=True))

    ##### change start to begin #####
    op.alter_column('relation', 'start_class_id', new_column_name='begin_class_id', existing_type=sa.Uuid)
    op.alter_column('relation', 'start_interface_id', new_column_name='begin_interface_id', existing_type=sa.Uuid)
    op.alter_column('relation', 'start_type', new_column_name='begin_type', existing_type=old_type)

    op.drop_constraint(op.f('uq_relation_unique_pair'), 'relation', type_='unique')
    op.create_unique_constraint('uq_relation_unique_pair', 'relation',
                                ['window_id', 'begin_class_id', 'begin_interface_id', 'end_class_id',
                                 'end_interface_id'])

    op.drop_constraint(op.f('relation_start_class_id_fkey'), 'relation', type_='foreignkey')
    op.drop_constraint(op.f('relation_start_interface_id_fkey'), 'relation', type_='foreignkey')
    op.create_foreign_key(None, 'relation', 'interface', ['begin_interface_id'], ['id'])
    op.create_foreign_key(None, 'relation', 'class', ['begin_class_id'], ['id'])

    op.drop_constraint(op.f('single_start_entity_check'), 'relation', type_='check')
    op.create_check_constraint(op.f('single_begin_entity_check'), 'relation',
                               '(begin_class_id IS NOT NULL AND begin_interface_id IS NULL) OR (begin_class_id IS NULL AND begin_interface_id IS NOT NULL)')


    ##### new enum #####
    new_type.create(op.get_bind(), checkfirst=False)

    op.execute("ALTER TABLE relation ALTER COLUMN end_type TYPE relationendtype USING ("
               "CASE end_type::text WHEN 'ONE_AND_ONLY_ONE' "
               "THEN 'ONE_ONLY_ONE' ELSE end_type::text END)::relationendtype")

    op.execute("ALTER TABLE relation ALTER COLUMN begin_type TYPE relationendtype USING ("
               "CASE begin_type::text WHEN 'ONE_AND_ONLY_ONE' "
               "THEN 'ONE_ONLY_ONE' ELSE begin_type::text END)::relationendtype")

    old_type.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('relation', 'type')
    relation_kind_type.drop(op.get_bind(), checkfirst=False)

    ##### downgrade begin to start #####
    op.alter_column('relation', 'begin_class_id', new_column_name='start_class_id', existing_type=sa.Uuid)
    op.alter_column('relation', 'begin_interface_id', new_column_name='start_interface_id', existing_type=sa.Uuid)
    op.alter_column('relation', 'begin_type', new_column_name='start_type', existing_type=new_type)

    op.drop_constraint(op.f('relation_begin_class_id_fkey'), 'relation', type_='foreignkey')
    op.drop_constraint(op.f('relation_begin_interface_id_fkey'), 'relation', type_='foreignkey')
    op.create_foreign_key(op.f('relation_start_interface_id_fkey'), 'relation', 'interface',
                          ['start_interface_id'],['id'])
    op.create_foreign_key(op.f('relation_start_class_id_fkey'), 'relation', 'class', ['start_class_id'], ['id'])

    op.drop_constraint('uq_relation_unique_pair', 'relation', type_='unique')
    op.create_unique_constraint(op.f('uq_relation_unique_pair'), 'relation',
                                ['window_id', 'start_class_id', 'start_interface_id', 'end_class_id',
                                 'end_interface_id'], postgresql_nulls_not_distinct=False)

    op.drop_constraint(op.f('single_begin_entity_check'), 'relation', type_='check')
    op.create_check_constraint(op.f('single_start_entity_check'), 'relation',
                               '(start_class_id IS NOT NULL AND start_interface_id IS NULL) OR (start_class_id IS NULL AND start_interface_id IS NOT NULL)')

    ##### new enum #####
    old_type.create(op.get_bind(), checkfirst=False)

    op.execute("ALTER TABLE relation ALTER COLUMN end_type TYPE relationtype USING ("
               "CASE end_type::text WHEN 'ONE_ONLY_ONE' "
               "THEN 'ONE_AND_ONLY_ONE' ELSE end_type::text END)::relationtype")

    op.execute("ALTER TABLE relation ALTER COLUMN start_type TYPE relationtype USING ("
               "CASE start_type::text WHEN 'ONE_ONLY_ONE' "
               "THEN 'ONE_AND_ONLY_ONE' ELSE start_type::text END)::relationtype")

    new_type.drop(op.get_bind(), checkfirst=False)

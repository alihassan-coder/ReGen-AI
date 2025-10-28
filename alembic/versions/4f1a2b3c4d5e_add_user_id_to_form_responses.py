"""add user_id to form_responses if missing

Revision ID: 4f1a2b3c4d5e
Revises: 9a77f189d752
Create Date: 2025-10-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f1a2b3c4d5e'
down_revision: Union[str, Sequence[str], None] = '9a77f189d752'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('form_responses')]

    if 'user_id' not in cols:
        with op.batch_alter_table('form_responses', schema=None) as batch_op:
            batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        # Add FK separately (batch_op.create_foreign_key not supported on some backends)
        op.create_foreign_key(
            'fk_form_responses_user_id', 'form_responses', 'users', ['user_id'], ['id'], ondelete='CASCADE'
        )
        # Optional index for faster filtering
        op.create_index('ix_form_responses_user_id', 'form_responses', ['user_id'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('form_responses')]

    if 'user_id' in cols:
        # Drop index and FK, then column
        try:
            op.drop_index('ix_form_responses_user_id', table_name='form_responses')
        except Exception:
            pass
        try:
            op.drop_constraint('fk_form_responses_user_id', 'form_responses', type_='foreignkey')
        except Exception:
            pass
        with op.batch_alter_table('form_responses', schema=None) as batch_op:
            batch_op.drop_column('user_id')



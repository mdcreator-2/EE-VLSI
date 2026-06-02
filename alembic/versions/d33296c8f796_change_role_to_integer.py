"""change_role_to_integer

Revision ID: d33296c8f796
Revises: 135ab7cb14d4
Create Date: 2026-06-03 03:18:56.782161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd33296c8f796'
down_revision: Union[str, Sequence[str], None] = '135ab7cb14d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'role')
    op.add_column('users', sa.Column('role', sa.Integer(), nullable=False, server_default='1'))
    # Drop the orphaned PostgreSQL ENUM type that's no longer used
    op.execute('DROP TYPE IF EXISTS roleenum')



def downgrade() -> None:
    op.drop_column('users', 'role')
    role_enum = postgresql.ENUM('STUDENT', 'CR', 'ADMIN', name='roleenum', create_type=True)
    role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', role_enum, nullable=False, server_default='STUDENT'))


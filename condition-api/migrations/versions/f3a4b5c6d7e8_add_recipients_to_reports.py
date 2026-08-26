"""add_recipients_to_reports

Revision ID: f3a4b5c6d7e8
Revises: 1c1f10d637dc
Create Date: 2026-08-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a4b5c6d7e8'
down_revision = '1c1f10d637dc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('reports', schema='condition') as batch_op:
        batch_op.add_column(sa.Column('recipients', sa.ARRAY(sa.Text()), nullable=True))


def downgrade():
    with op.batch_alter_table('reports', schema='condition') as batch_op:
        batch_op.drop_column('recipients')

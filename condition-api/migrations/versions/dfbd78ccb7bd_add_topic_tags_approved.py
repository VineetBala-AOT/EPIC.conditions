"""add_topic_tags_approved

Revision ID: dfbd78ccb7bd
Revises: 1041c57bc31f
Create Date: 2024-11-09 22:16:30.384999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfbd78ccb7bd'
down_revision = '1041c57bc31f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'conditions',
        sa.Column('is_topic_tags_approved', sa.Boolean(), nullable=True),
        schema='condition'
    )
    op.add_column(
        'condition_requirements',
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        schema='condition'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('conditions', 'is_topic_tags_approved', schema='condition')
    op.drop_column('condition_requirements', 'is_approved', schema='condition')
    # ### end Alembic commands ###
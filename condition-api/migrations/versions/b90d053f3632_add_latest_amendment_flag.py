"""add_latest_amendment_flag

Revision ID: b90d053f3632
Revises: e4912bf17735
Create Date: 2025-01-13 21:07:54.472773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b90d053f3632'
down_revision = 'e4912bf17735'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("documents", schema='condition') as batch_op:
        batch_op.add_column(sa.Column('is_latest_amendment_added', sa.Boolean(), nullable=True))
    op.create_index('ix_project_id', 'projects', ['project_id'], unique=False, schema='condition')
    op.create_index('ix_document_type_id', 'document_types', ['id'], unique=False, schema='condition')
    op.create_index('ix_document_category_id', 'document_categories', ['id'], unique=False, schema='condition')
    op.create_index('ix_document_id', 'documents', ['id'], unique=False, schema='condition')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("documents", schema='condition') as batch_op:
        batch_op.drop_column("is_latest_amendment_added")
    op.drop_index('ix_project_id', table_name='projects', schema='condition')
    op.drop_index('ix_document_type_id', table_name='document_types', schema='condition')
    op.drop_index('ix_document_category_id', table_name='document_categories', schema='condition')
    op.drop_index('ix_document_id', table_name='documents', schema='condition')
    # ### end Alembic commands ###
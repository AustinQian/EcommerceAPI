"""Add is_groupbuy column to Product model

Revision ID: dbd0524124e2
Revises: 2eb7107bff8f
Create Date: 2025-03-28 15:15:04.505613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbd0524124e2'
down_revision = '2eb7107bff8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_groupbuy', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('is_groupbuy')

    # ### end Alembic commands ###

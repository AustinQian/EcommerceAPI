"""add created_at to cart

Revision ID: 2eb7107bff8f
Revises: ce3aee35c230
Create Date: 2025-03-28 11:16:43.435072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2eb7107bff8f'
down_revision = 'ce3aee35c230'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('checked', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart', schema=None) as batch_op:
        batch_op.drop_column('checked')
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###

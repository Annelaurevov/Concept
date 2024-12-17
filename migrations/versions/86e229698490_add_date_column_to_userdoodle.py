"""Add date column to UserDoodle

Revision ID: 86e229698490
Revises: c455d026f709
Create Date: 2024-12-17 22:14:24.607821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86e229698490'
down_revision = 'c455d026f709'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_doodles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_doodles', schema=None) as batch_op:
        batch_op.drop_column('date')

    # ### end Alembic commands ###

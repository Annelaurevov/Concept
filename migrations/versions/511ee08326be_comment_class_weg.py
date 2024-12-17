"""comment class weg

Revision ID: 511ee08326be
Revises: 84f50ae93f51
Create Date: 2024-12-16 19:04:20.462665

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '511ee08326be'
down_revision = '84f50ae93f51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    with op.batch_alter_table('user_doodles', schema=None) as batch_op:
        batch_op.drop_constraint('user_doodles_doodle_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'doodles', ['doodle_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_doodles', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_doodles_doodle_id_fkey', 'doodles', ['doodle_id'], ['id'], ondelete='CASCADE')

    op.create_table('comments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('item_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('item_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('text', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='comments_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='comments_pkey')
    )
    # ### end Alembic commands ###
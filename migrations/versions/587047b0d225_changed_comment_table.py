"""changed comment table

Revision ID: 587047b0d225
Revises: e32a9b2a2723
Create Date: 2023-07-27 18:17:24.902194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '587047b0d225'
down_revision = 'e32a9b2a2723'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('announcements', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint(None, 'announcements', type_='foreignkey')
    op.create_foreign_key(None, 'announcements', 'users', ['user_id'], ['id'])
    op.drop_column('announcements', 'user')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('announcements', sa.Column('user', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'announcements', type_='foreignkey')
    op.create_foreign_key(None, 'announcements', 'users', ['user'], ['id'])
    op.drop_column('announcements', 'user_id')
    # ### end Alembic commands ###
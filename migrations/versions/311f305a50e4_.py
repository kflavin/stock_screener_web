"""empty message

Revision ID: 311f305a50e4
Revises: 10b24b09b9df
Create Date: 2017-10-04 19:56:44.870054

"""

# revision identifiers, used by Alembic.
revision = '311f305a50e4'
down_revision = '10b24b09b9df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'company', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'company', type_='foreignkey')
    op.drop_column('company', 'user_id')
    # ### end Alembic commands ###

"""empty message

Revision ID: 85674cb38cf9
Revises: 3e20fa1bea82
Create Date: 2016-11-18 23:23:42.110182

"""

# revision identifiers, used by Alembic.
revision = '85674cb38cf9'
down_revision = '3e20fa1bea82'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('industry', sa.String(length=50), nullable=True))
    op.add_column('company', sa.Column('sector', sa.String(length=50), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'sector')
    op.drop_column('company', 'industry')
    ### end Alembic commands ###

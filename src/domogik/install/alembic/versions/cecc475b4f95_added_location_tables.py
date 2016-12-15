"""Added location tables

Revision ID: cecc475b4f95
Revises: f9da78a77717
Create Date: 2016-12-15 14:14:24.163763

"""

# revision identifiers, used by Alembic.
revision = 'cecc475b4f95'
down_revision = 'f9da78a77717'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('core_location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(length=32), autoincrement=False, nullable=False),
    sa.Column('isHome', sa.Boolean(), nullable=False),
    sa.Column('type', sa.Unicode(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_character_set='utf8',
    mysql_engine='InnoDB'
    )
    op.create_table('core_location_param',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('key', sa.Unicode(length=32), autoincrement=False, nullable=False),
    sa.Column('value', sa.Unicode(length=255), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['core_location.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id', 'key'),
    mysql_character_set='utf8',
    mysql_engine='InnoDB'
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('core_location_param')
    op.drop_table('core_location')
    ### end Alembic commands ###

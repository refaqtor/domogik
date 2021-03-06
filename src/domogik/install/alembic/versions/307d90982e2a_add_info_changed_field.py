"""Add info_changed field

Revision ID: 307d90982e2a
Revises: 2f736b443fd2
Create Date: 2016-10-09 20:03:14.826643

"""

# revision identifiers, used by Alembic.
revision = '307d90982e2a'
down_revision = '2f736b443fd2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('core_device', sa.Column('info_changed', sa.DateTime(), nullable=False))
    op.create_index(op.f('ix_core_device_info_changed'), 'core_device', ['info_changed'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_core_device_info_changed'), table_name='core_device')
    op.drop_column('core_device', 'info_changed')
    ### end Alembic commands ###

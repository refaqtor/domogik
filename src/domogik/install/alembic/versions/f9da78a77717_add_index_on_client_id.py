"""Add index on client_id

Revision ID: f9da78a77717
Revises: 307d90982e2a
Create Date: 2016-11-23 20:42:32.180746

"""

# revision identifiers, used by Alembic.
revision = 'f9da78a77717'
down_revision = '307d90982e2a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_core_device_client_id'), 'core_device', ['client_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_core_device_client_id'), table_name='core_device')
    ### end Alembic commands ###

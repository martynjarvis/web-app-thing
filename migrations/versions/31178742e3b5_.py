"""empty message

Revision ID: 31178742e3b5
Revises: 1cf99137d64
Create Date: 2015-07-11 18:24:39.644798

"""

# revision identifiers, used by Alembic.
revision = '31178742e3b5'
down_revision = '1cf99137d64'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crest_station',
    sa.Column('facilityID', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('solarSystem_id', sa.Integer(), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('facilityID')
    )
    op.create_table('crest_region',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('href', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crest_system',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('href', sa.String(length=80), nullable=True),
    sa.Column('region_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('crest_system')
    op.drop_table('crest_region')
    op.drop_table('crest_station')
    ### end Alembic commands ###
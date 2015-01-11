"""empty message

Revision ID: 50c6927cfcd5
Revises: 28d74cae9b18
Create Date: 2015-01-10 19:20:51.510154

"""

# revision identifiers, used by Alembic.
revision = '50c6927cfcd5'
down_revision = '28d74cae9b18'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_corporation',
    sa.Column('corporationID', sa.Integer(), nullable=False),
    sa.Column('corporationName', sa.String(length=80), nullable=True),
    sa.Column('ticker', sa.String(length=5), nullable=True),
    sa.Column('ceoID', sa.Integer(), nullable=True),
    sa.Column('ceoName', sa.String(length=80), nullable=True),
    sa.Column('stationID', sa.Integer(), nullable=True),
    sa.Column('stationName', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=80), nullable=True),
    sa.Column('url', sa.String(length=80), nullable=True),
    sa.Column('allianceID', sa.Integer(), nullable=True),
    sa.Column('factionID', sa.Integer(), nullable=True),
    sa.Column('taxRate', sa.Float(), nullable=True),
    sa.Column('memberCount', sa.Integer(), nullable=True),
    sa.Column('memberLimit', sa.Integer(), nullable=True),
    sa.Column('shares', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('corporationID')
    )
    op.create_table('api_apicorporation',
    sa.Column('corporationID', sa.Integer(), nullable=True),
    sa.Column('keyID', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['corporationID'], ['api_corporation.corporationID'], ),
    sa.ForeignKeyConstraint(['keyID'], ['api_api.keyID'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('api_apicorporation')
    op.drop_table('api_corporation')
    ### end Alembic commands ###

"""empty message

Revision ID: db5012d366b
Revises: 4bb89a1480e8
Create Date: 2014-07-28 23:13:15.229000

"""

# revision identifiers, used by Alembic.
revision = 'db5012d366b'
down_revision = '4bb89a1480e8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('RawMaterial',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('parent_task_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_task_id'], ['Task.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['TypeID.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('RawMaterial')
    ### end Alembic commands ###
"""empty message

Revision ID: 4bb89a1480e8
Revises: 5848d14a7db
Create Date: 2014-07-27 17:23:25.585000

"""

# revision identifiers, used by Alembic.
revision = '4bb89a1480e8'
down_revision = '5848d14a7db'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Blueprint',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('production_limit', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('TypeID',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('graphic_id', sa.Integer(), nullable=True),
    sa.Column('radius', sa.Float(), nullable=True),
    sa.Column('sound_id', sa.Integer(), nullable=True),
    sa.Column('icon_id', sa.Integer(), nullable=True),
    sa.Column('faction_id', sa.Integer(), nullable=True),
    sa.Column('volume', sa.Float(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('output_id', sa.Integer(), nullable=False),
    sa.Column('output_quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['output_id'], ['TypeID.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('blueprint_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['blueprint_id'], ['Blueprint.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('probability', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['Activity.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['TypeID.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('output_id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('parent_task_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('output_quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['Activity.id'], ),
    sa.ForeignKeyConstraint(['output_id'], ['TypeID.id'], ),
    sa.ForeignKeyConstraint(['parent_task_id'], ['Task.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Material',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('consume', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activity.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['TypeID.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Material')
    op.drop_table('Task')
    op.drop_table('Product')
    op.drop_table('Activity')
    op.drop_table('Project')
    op.drop_table('TypeID')
    op.drop_table('Blueprint')
    ### end Alembic commands ###
"""empty message

Revision ID: 83d80f9938d3
Revises: bf7473dbd8fd
Create Date: 2019-10-15 11:16:37.796439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83d80f9938d3'
down_revision = 'bf7473dbd8fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fields',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('field_name', sa.String(), nullable=True),
    sa.Column('field_type', sa.String(), nullable=True),
    sa.Column('field_unit', sa.String(), nullable=True),
    sa.Column('field_order', sa.Integer(), nullable=True),
    sa.Column('is_historic', sa.Boolean(), nullable=False),
    sa.Column('is_remembered', sa.Boolean(), nullable=False),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('tanks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tank_name', sa.String(), nullable=True),
    sa.Column('tank_type', sa.String(), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('multiplier', sa.Float(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('users',
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('user_type', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('well_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_name', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('group_latest_production_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('wells',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('well_name', sa.String(), nullable=True),
    sa.Column('well_type', sa.String(), nullable=True),
    sa.Column('well_alias', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('latest_production_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('meters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('meter_name', sa.String(), nullable=True),
    sa.Column('meter_order', sa.Integer(), nullable=True),
    sa.Column('product_type', sa.String(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('id', 'well_id'),
    schema='iwell'
    )
    op.create_table('production_daily',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('produced_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('oil', sa.Float(), nullable=False),
    sa.Column('gas', sa.Float(), nullable=False),
    sa.Column('water', sa.Float(), nullable=False),
    sa.Column('is_operating', sa.Boolean(), nullable=True),
    sa.Column('hours_on', sa.Integer(), nullable=False),
    sa.Column('normal_hours_on', sa.Integer(), nullable=False),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['updated_by'], ['iwell.users.id'], ),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('tank_readings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tank_id', sa.Integer(), nullable=False),
    sa.Column('reading_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('cut_feet', sa.Float(), nullable=True),
    sa.Column('cut_inches', sa.Float(), nullable=True),
    sa.Column('top_feet', sa.Float(), nullable=True),
    sa.Column('top_inches', sa.Float(), nullable=True),
    sa.Column('previous_cut_feet', sa.Float(), nullable=True),
    sa.Column('previous_cut_inches', sa.Float(), nullable=True),
    sa.Column('previous_top_feet', sa.Float(), nullable=True),
    sa.Column('previous_top_inches', sa.Float(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['tank_id'], ['iwell.tanks.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['iwell.users.id'], ),
    sa.PrimaryKeyConstraint('id', 'tank_id'),
    schema='iwell'
    )
    op.create_table('well_fields',
    sa.Column('field_id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['field_id'], ['iwell.fields.id'], ),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('field_id', 'well_id'),
    schema='iwell'
    )
    op.create_table('well_group_wells',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['iwell.well_groups.id'], ),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'well_id'),
    schema='iwell'
    )
    op.create_table('well_notes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('noted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('author', sa.Integer(), nullable=True),
    sa.Column('is_pumper_content', sa.Boolean(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['iwell.users.id'], ),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('id', 'well_id'),
    schema='iwell'
    )
    op.create_table('well_tanks',
    sa.Column('tank_id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['tank_id'], ['iwell.tanks.id'], ),
    sa.ForeignKeyConstraint(['well_id'], ['iwell.wells.id'], ),
    sa.PrimaryKeyConstraint('tank_id', 'well_id'),
    schema='iwell'
    )
    op.create_table('field_values',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('field_id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('reading_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['field_id', 'well_id'], ['iwell.well_fields.field_id', 'iwell.well_fields.well_id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['iwell.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('meter_readings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meter_id', sa.Integer(), nullable=False),
    sa.Column('well_id', sa.Integer(), nullable=False),
    sa.Column('reading_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('previous_value', sa.Float(), nullable=False),
    sa.Column('updated_by', sa.Integer(), nullable=False),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['meter_id', 'well_id'], ['iwell.meters.id', 'iwell.meters.well_id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['iwell.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    op.create_table('run_tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tank_id', sa.Integer(), nullable=False),
    sa.Column('reading_id', sa.Integer(), nullable=False),
    sa.Column('reading_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('run_ticket_number', sa.String(), nullable=False),
    sa.Column('total', sa.Float(), nullable=True),
    sa.Column('product_type', sa.String(), nullable=False),
    sa.Column('picture_url', sa.String(), nullable=False),
    sa.Column('comments', sa.String(), nullable=False),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('iwell_created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('iwell_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['tank_id', 'reading_id'], ['iwell.tank_readings.tank_id', 'iwell.tank_readings.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['iwell.users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='iwell'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('run_tickets', schema='iwell')
    op.drop_table('meter_readings', schema='iwell')
    op.drop_table('field_values', schema='iwell')
    op.drop_table('well_tanks', schema='iwell')
    op.drop_table('well_notes', schema='iwell')
    op.drop_table('well_group_wells', schema='iwell')
    op.drop_table('well_fields', schema='iwell')
    op.drop_table('tank_readings', schema='iwell')
    op.drop_table('production_daily', schema='iwell')
    op.drop_table('meters', schema='iwell')
    op.drop_table('wells', schema='iwell')
    op.drop_table('well_groups', schema='iwell')
    op.drop_table('users', schema='iwell')
    op.drop_table('tanks', schema='iwell')
    op.drop_table('fields', schema='iwell')
    # ### end Alembic commands ###

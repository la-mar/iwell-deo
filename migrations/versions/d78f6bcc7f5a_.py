"""empty message

Revision ID: d78f6bcc7f5a
Revises: cf431d1cf0e1
Create Date: 2019-11-21 09:29:20.938520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d78f6bcc7f5a"
down_revision = "cf431d1cf0e1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create view vw_meter_readings as
        select
            wells.id as well_id,
            well_name,
            well_type,
            well_alias,
            is_active,
            latest_production_time,
            meters.id as meter_id,
            meter_name,
            meter_order,
            product_type,
            mr.id as meter_reading_id,
            reading_at,
            value,
            previous_value,
            updated_by,
            mr.iwell_created_at,
            mr.iwell_updated_at,
            mr.created_at,
            mr.updated_at
        from wells
                inner join meters on wells.id = meters.well_id
                inner join meter_readings mr on meters.id = mr.meter_id and meters.well_id = mr.well_id
    """
    )


def downgrade():
    op.execute("""drop view vw_meter_readings""")

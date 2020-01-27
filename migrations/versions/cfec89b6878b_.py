"""empty message

Revision ID: cfec89b6878b
Revises: 8d5aa15ebdce
Create Date: 2020-01-27 15:21:06.146355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cfec89b6878b"
down_revision = "8d5aa15ebdce"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create or replace view vw_gauge_times as
        select
            id,
            field_id,
            well_id,
            reading_at,
            value,
            parse_time(value) gauge_time_local,
            (reading_at at time zone 'US/Central')::date as reading_at_local,
            (((reading_at at time zone 'US/Central')::date)::text || ' ' || parse_time(value))::timestamp as gauge_at_local,
            (((reading_at at time zone 'US/Central')::date)::text || ' ' || parse_time(value))::timestamp at time zone 'US/Central' at time zone 'UTC' as gauge_at,
            updated_by,
            iwell_created_at,
            iwell_updated_at,
            created_at,
            updated_at
        from field_values where field_id = 3051;

        create view vw_production_with_gauge_time as
        select
            well_name,
            well_type,
            well_alias,
            is_active,
            latest_production_time,
            p.id,
            p.well_id,
            produced_at,
            oil,
            gas,
            water,
            reported_date,
            gauge_time_local,
            gauge_at_local,
            gauge_at,
            is_operating,
            hours_on,
            normal_hours_on
        from vw_production p
        left outer join vw_gauge_times g on p.reported_date::date = g.gauge_at_local::date and p.well_id = g.well_id
        order by p.reported_date desc;
    """
    )


def downgrade():
    op.execute(
        """
        drop view vw_gauge_times;
        drop view vw_production_with_gauge_time;
        """
    )

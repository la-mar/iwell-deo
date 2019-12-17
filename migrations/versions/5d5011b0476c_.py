"""empty message

Revision ID: 5d5011b0476c
Revises: 70c7338dd26c
Create Date: 2019-11-06 09:23:54.017483

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d5011b0476c"
down_revision = "70c7338dd26c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            create view vw_tank_volumes as
            with ft_to_inches as (
                select
                    tr.reading_at as measured_at,
                    tr.tank_id,
                    tr.top_inches + (top_feet * 12) as top_inches,
                    tr.cut_inches + (cut_feet * 12) as bottom_inches,
                    t.multiplier as bbl_inch_factor
                from tank_readings tr
                        inner join tanks t on tr.tank_id = t.id
            ),
            volumes as (
                select
                    measured_at,
                    tank_id,
                    top_inches,
                    bottom_inches,
                    bbl_inch_factor,
                    round((((top_inches - bottom_inches) * bbl_inch_factor))::numeric,
                            2) as oil_volume,
                    round(((bottom_inches * bbl_inch_factor))::numeric, 2) as water_volume
                from ft_to_inches
            ),
            lag_calcs as (
                select
                    measured_at,
                    tank_id,
                    top_inches,
                    bottom_inches,
                    bbl_inch_factor,
                    oil_volume,
                    water_volume,
                    lag(oil_volume, 1)
                    over (partition by tank_id order by measured_at) as oil_volume_lag1,
                    lag(water_volume, 1)
                    over (partition by tank_id order by measured_at) as water_volume_lag1,
                    lag(measured_at, 1)
                    over (partition by tank_id order by measured_at) as measured_at_lag1
                from volumes
            ),
            deltas as (
                select
                    measured_at,
                    tank_id,
                    top_inches,
                    bottom_inches,
                    bbl_inch_factor,
                    oil_volume,
                    water_volume,
                    oil_volume_lag1,
                    water_volume_lag1,
                    measured_at_lag1,
                    (lag_calcs.oil_volume - lag_calcs.oil_volume_lag1) as delta_oil_volume,
                    (lag_calcs.water_volume - lag_calcs.water_volume_lag1) as delta_water_volume,
                    date_part('epoch'::text,
                                (lag_calcs.measured_at - lag_calcs.measured_at_lag1)) as delta_seconds
                from lag_calcs
            ),
            rates as (
                select
                    measured_at,
                    tank_id,
                    top_inches,
                    bottom_inches,
                    bbl_inch_factor,
                    oil_volume,
                    water_volume,
                    oil_volume_lag1,
                    water_volume_lag1,
                    measured_at_lag1,
                    delta_oil_volume,
                    delta_water_volume,
                    delta_seconds,
                    round((delta_oil_volume / (delta_seconds)::numeric), 5) as delta_oil_rate,
                    round((delta_water_volume / (delta_seconds)::numeric), 5) as delta_water_rate,
                    (- round(((((bbl_inch_factor * (2)::double precision) *
                                (delta_seconds / (60)::double precision)) / delta_seconds))::numeric,
                            5)) as hauling_threshold_rate
            --         ((- bbl_inch_factor) * (2)::double precision) as delta_volume_lower_bound
                from deltas
            )
            select
                measured_at,
                w.id as well_id,
                well_name,
                well_type,
                t.id as tank_id,
                tank_name,
                tank_type,
                capacity,
                multiplier,
                top_inches,
                bottom_inches,
                bbl_inch_factor,
                oil_volume,
                water_volume,
                oil_volume_lag1,
                water_volume_lag1,
                measured_at_lag1,
                delta_oil_volume,
                delta_water_volume,
                delta_seconds
            from deltas d
            inner join tanks t on d.tank_id = t.id
            inner join well_tanks wt on wt.tank_id = t.id
            inner join wells w on w.id = wt.well_id;
    """
    )


def downgrade():
    op.execute("""drop view vw_tank_volumes;""")

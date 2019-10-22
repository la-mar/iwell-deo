"""empty message

Revision ID: a1bbfc2ee006
Revises: a3391c68e2b9
Create Date: 2019-10-21 11:20:47.285419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1bbfc2ee006"
down_revision = "a3391c68e2b9"
branch_labels = None
depends_on = None


def upgrade():

    op.execute(
        """
        create view vw_meter_readings
                    (well_id, wellname, well_type, well_alias, is_active, latest_production_time, meter_id, meter_name,
                    meter_order, product_type, reading_id, reading_at, value, previous_value)
        as
        select
            wells.id as well_id,
            wells.well_name as wellname,
            wells.well_type,
            wells.well_alias,
            wells.is_active,
            wells.latest_production_time,
            meters.id as meter_id,
            meters.meter_name,
            meters.meter_order,
            meters.product_type,
            meter_readings.id as reading_id,
            meter_readings.reading_at,
            meter_readings.value,
            meter_readings.previous_value
        from ((wells
            join meters on ((wells.id = meters.well_id)))
                join meter_readings
                    on (((meters.well_id = meter_readings.well_id) and (meters.id = meter_readings.meter_id))));
    """
    )
    op.execute(
        """
        create view vw_production
        as
        select
            well_name,
            well_type,
            well_alias,
            is_active,
            latest_production_time,
            production.*
        from production
                inner join wells
                            on production.well_id = wells.id;
    """
    )
    op.execute(
        """
        create view vw_run_tickets
        as
        select
            wells.id as well_id
        , wells.well_name as wellname
        , wells.well_type
        , wells.well_alias
        , wells.is_active
        , wells.latest_production_time
        , tanks.tank_name
        , tanks.id as tank_id
        , tanks.tank_type
        , tanks.capacity
        , tanks.multiplier
        , tank_readings.id
        , tank_readings.reading_at
        , tank_readings.cut_feet
        , tank_readings.cut_inches
        , tank_readings.top_feet
        , tank_readings.top_inches
        , tank_readings.previous_cut_feet
        , tank_readings.previous_cut_inches
        , tank_readings.previous_top_feet
        , tank_readings.previous_top_inches
        , run_tickets.id as run_ticket_id
        , run_tickets.run_ticket_number
        , run_tickets.total
        , run_tickets.product_type
        , run_tickets.picture_url
        , run_tickets.comments
        from wells
                inner join well_tanks
                            on wells.id = well_tanks.well_id
                inner join tanks
                            on well_tanks.tank_id = tanks.id
                inner join tank_readings
                            on tanks.id = tank_readings.tank_id
                inner join run_tickets
                            on tank_readings.tank_id = run_tickets.tank_id
                                and tank_readings.id = run_tickets.reading_id;
    """
    )
    op.execute(
        """
        create view vw_tank_readings
        as
        select
            wells.id as well_id
        , wells.well_name as wellname
        , wells.well_type
        , wells.well_alias
        , wells.is_active
        , wells.latest_production_time
        , tanks.tank_name
        , tanks.id as tank_id
        , tanks.tank_type
        , tanks.capacity
        , tanks.multiplier
        , tank_readings.id
        , tank_readings.reading_at
        , tank_readings.cut_feet
        , tank_readings.cut_inches
        , tank_readings.top_feet
        , tank_readings.top_inches
        , tank_readings.previous_cut_feet
        , tank_readings.previous_cut_inches
        , tank_readings.previous_top_feet
        , tank_readings.previous_top_inches
        from wells
                inner join well_tanks
                            on wells.id = well_tanks.well_id
                inner join tanks
                            on well_tanks.tank_id = tanks.id
                inner join tank_readings
                            on tanks.id = tank_readings.tank_id;
    """
    )
    op.execute(
        """
        create view vw_tanks
        as
        select
            wells.id as well_id
        , wells.well_name as wellname
        , wells.well_type
        , wells.well_alias
        , wells.is_active
        , wells.latest_production_time
        , tanks.id as tank_id
        , tanks.tank_name
        , tanks.tank_type
        , tanks.capacity
        , tanks.multiplier
        from wells
                inner join well_tanks
                            on wells.id = well_tanks.well_id
                inner join tanks
                            on well_tanks.tank_id = tanks.id;
    """
    )


def downgrade():
    op.execute("""drop view vw_meter_readings;""")
    op.execute("""drop view vw_production;""")
    op.execute("""drop view vw_run_tickets;""")
    op.execute("""drop view vw_tank_readings;""")
    op.execute("""drop view vw_tanks;""")


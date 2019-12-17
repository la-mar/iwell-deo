"""empty message

Revision ID: e4ad63130045
Revises: c703573fa13d
Create Date: 2019-12-06 21:45:47.487060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4ad63130045"
down_revision = "c703573fa13d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            create or replace view vw_gauge_time as
            with c as (
                select
                    fv.reading_at,
                    w.id as well_id,
                    w.well_name,
                    f.field_name,
                    fv.value,
                    (timezone('US/Central'::text, reading_at))::date as reading_date_local,
                    parse_time(value) as reading_time_parsed_local,
                    timezone('US/Central'::text, reading_at) as reading_at_local
                from field_values fv
                        join wells w on fv.well_id = w.id
                        join fields f on fv.field_id = f.id
                where field_name = 'Time of Gauge')
            , c2 as (
                select
                    reading_at,
                    well_id,
                    well_name,
                    field_name,
                    value,
                    reading_date_local,
                    reading_time_parsed_local,
                    reading_at_local,
                    (((reading_date_local || ' '::text) ||
                    (reading_time_parsed_local)::text))::timestamp without time zone as reading_datetime_parsed_local,
                    ((((reading_date_local || ' '::text) ||
                    (reading_time_parsed_local)::text))::timestamp without time zone +
                    '24:00:00'::interval) as reading_datetime_parsed_local_plus24hours
                from c)
            , c3 as (
                select
                    c2.reading_at,
                    c2.well_id,
                    well_name,
                    field_name,
                    value as original_value,
                    c2.reading_date_local,
                    c2.reading_time_parsed_local,
                    c2.reading_at_local,
                    reading_datetime_parsed_local,
                    reading_datetime_parsed_local_plus24hours,
                    timezone('UTC'::text, reading_datetime_parsed_local) as reading_datetime,
                    timezone('UTC'::text, reading_datetime_parsed_local_plus24hours) as reading_datetime_plus24hours,
                    ticket_date,
                    (timezone('US/Central'::text, (t.ticket_date)::timestamp with time zone))::date as ticket_date_local,
                    tank_name,
                    tank_id,
                    tank_type,
                    capacity,
                    multiplier,
                    cut_feet,
                    cut_inches,
                    top_feet,
                    top_inches,
                    previous_cut_feet,
                    previous_cut_inches,
                    previous_top_feet,
                    previous_top_inches,
                    run_ticket_id,
                    run_ticket_number,
                    total,
                    product_type,
                    picture_url,
                    comments
                from c2
                    left join lateral ( select
                                            rt.well_id,
                                            rt.wellname,
                                            rt.well_type,
                                            rt.well_alias,
                                            rt.is_active,
                                            rt.latest_production_time,
                                            rt.tank_name,
                                            rt.tank_id,
                                            rt.tank_type,
                                            rt.capacity,
                                            rt.multiplier,
                                            rt.id,
                                            rt.reading_at,
                                            rt.cut_feet,
                                            rt.cut_inches,
                                            rt.top_feet,
                                            rt.top_inches,
                                            rt.previous_cut_feet,
                                            rt.previous_cut_inches,
                                            rt.previous_top_feet,
                                            rt.previous_top_inches,
                                            rt.run_ticket_id,
                                            rt.run_ticket_number,
                                            rt.total,
                                            rt.product_type,
                                            rt.picture_url,
                                            rt.comments,
                                            rt.ticket_date
                                        from vw_run_tickets rt
                                        where ((rt.well_id = c2.well_id) and
                                                (timezone('US/Central'::text, (rt.ticket_date)::timestamp with time zone) >=
                                                c2.reading_datetime_parsed_local) and
                                                (timezone('US/Central'::text, (rt.ticket_date)::timestamp with time zone) <=
                                                c2.reading_datetime_parsed_local_plus24hours))) t on (true))
            select
                reading_at,
                reading_at_local,
                well_id,
                well_name,
                field_name,
                original_value,
                reading_date_local,
                reading_time_parsed_local as gauge_time_local,
                reading_datetime_parsed_local as gauge_at_local,
                reading_datetime_parsed_local_plus24hours as gauge_at_local_plus24hours,
                ticket_date_local,
                ticket_date,
                tank_name,
                tank_id,
                tank_type,
                capacity,
                multiplier,
                cut_feet,
                cut_inches,
                top_feet,
                top_inches,
                previous_cut_feet,
                previous_cut_inches,
                previous_top_feet,
                previous_top_inches,
                run_ticket_id,
                run_ticket_number,
                total,
                product_type,
                picture_url,
                comments
            from c3;
    """
    )


def downgrade():
    op.execute("""drop view vw_gauge_time""")

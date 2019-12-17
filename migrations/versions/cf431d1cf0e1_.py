"""empty message

Revision ID: cf431d1cf0e1
Revises: 5d5011b0476c
Create Date: 2019-11-15 09:24:25.980224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cf431d1cf0e1"
down_revision = "5d5011b0476c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create view vw_run_tickets_by_gauge_time as (
        with parsed as (
            select
                (noted_at at time zone 'US/Central')::timestamp::date as noted_date_local,
                parse_time(message) as noted_time_parsed_local,
                noted_at at time zone 'US/Central' as noted_at_local,
                *
            from well_notes
        ),
            parsed2 as (
                select
                    noted_date_local,
                    noted_time_parsed_local,
                    (noted_date_local || ' ' || noted_time_parsed_local)::timestamp  as noted_datetime_parsed_local,
                    (noted_date_local || ' ' || noted_time_parsed_local)::timestamp+
                    interval '24 hours' as noted_datetime_parsed_local_plus24hours,
                    noted_at_local,
                    id,
                    well_id,
                    noted_at,
                    message,
                    author,
                    is_pumper_content,
                    iwell_created_at,
                    iwell_updated_at,
                    created_at,
                    updated_at
                from parsed
            )
        select
            p.id as note_id,
            p.well_id,
            ticket_date,
            noted_at::date as noted_at,
            p.noted_datetime_parsed_local at time zone 'UTC' as noted_datetime,
            p.noted_datetime_parsed_local_plus24hours at time zone 'UTC' as noted_datetime_plus24hours,
            (ticket_date at time zone 'US/Central')::date as ticket_date_local,
            p.noted_date_local,
            p.noted_time_parsed_local as noted_time_local,
            p.noted_datetime_parsed_local as noted_datetime_local,
            p.noted_datetime_parsed_local_plus24hours,
            p.noted_at_local,
            message,
            author,
            is_pumper_content,
            tank_name,
            tank_id,
            tank_type,
            capacity,
            multiplier,
            reading_at,
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
            comments,
            wells.id,
            well_name,
            wells.well_type,
            wells.well_alias,
            wells.is_active,
            wells.latest_production_time
        from parsed2 as p
                left outer join wells on p.well_id = wells.id
                left join lateral ( select *
                                    from vw_run_tickets rt
                                    where rt.well_id = p.well_id
                                    and rt.ticket_date at time zone 'US/Central' >= p.noted_datetime_parsed_local
                                    and rt.ticket_date at time zone 'US/Central' <= p.noted_datetime_parsed_local_plus24hours) t on true
        order by ticket_date asc);
    """
    )


def downgrade():
    op.execute("""drop view vw.run_tickets_by_gauge;""")
